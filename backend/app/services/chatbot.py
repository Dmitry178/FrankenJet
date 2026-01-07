import asyncio
import re
import unicodedata

from uuid import UUID

from app.config.app import GIGACHAT_USER_MESSAGE_MAX_SIZE
from app.config.chatbot import ChatBotSettingsManager
from app.core import es_manager, vectorizer_manager
from app.core.db_manager import DBManager
from app.core.gigachat import gigachat_api
from app.core.logs import logger
from app.core.ws_manager import WSManager
from app.db.models.chatbot import MessageIntent
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.gigachat import SGigaChatAnswer
from app.services.ragbot import RagBotService


class ChatBotServices:

    db: DBManager | None

    intent_mapper = {
        str(MessageIntent.intent_greeting): "Приветствую. Вы можете задать вопрос по теме авиации.",
        str(MessageIntent.intent_offtopic): "Я могу отвечать только по теме авиации.",
        str(MessageIntent.intent_timeout): "⚠️ Превышено время ожидания ответа от сервера.",
        str(MessageIntent.intent_blacklist): "Я могу отвечать только по теме авиации.",
        str(MessageIntent.intent_spam): "Я могу отвечать только по теме авиации.",
    }

    REGEX = re.compile(r'\s+')

    def __init__(
            self,
            db: DBManager | None = None,
            ws_manager: WSManager | None = None,
            bot_settings: ChatBotSettingsManager | None = None,
    ) -> None:
        self.db = db
        self.ws_manager = ws_manager
        self.bot_settings = bot_settings  # менеджер настроек бота

    @handle_basic_db_errors
    async def get_history_for_bot(self, chat_id: UUID) -> list:
        """
        Получение истории чата пользователя для отправки на frontend
        """

        result = await self.db.chatbot.history.get_user_history(chat_id)
        return result[::-1]

    @handle_basic_db_errors
    async def get_history_for_api(self, chat_id: UUID, intent: str | None = None) -> list:
        """
        Получение истории чата пользователя для отправки в LLM по API
        """

        history = []
        raw_history = await self.db.chatbot.history.get_user_history(chat_id, intent=intent, limit=4)

        for item in raw_history[::-1]:
            if message := item.get("message"):
                history.append({"role": "user", "content": message})
            if answer := item.get("answer"):
                history.append({"role": "assistant", "content": answer})

        return history

    async def _check_limits(self, chat_id: UUID, message: str) -> bool:
        """
        Проверка длины сообщения лимитов по токенам
        """

        if not message:
            return False

        try:
            # проверка длины сообщения
            if len(message) > GIGACHAT_USER_MESSAGE_MAX_SIZE:
                await self.ws_manager.send_message_to_connection(
                    chat_id,
                    f"⚠️ Превышение максимальной длины сообщения в {GIGACHAT_USER_MESSAGE_MAX_SIZE} символов"
                )
                return False

            # проверка оставшегося количества токенов
            count_tokens = await self.db.chatbot.history.count_daily_tokens(chat_id)
            settings = await self.bot_settings.get_settings()

            if count_tokens.get("user_daily_tokens", 0) > settings.user_daily_tokens:
                await self.ws_manager.send_message_to_connection(chat_id, "⚠️ Превышение лимита токенов")
                return False

            if count_tokens.get("total_daily_tokens", 0) > settings.total_daily_tokens:
                await self.ws_manager.send_message_to_connection(chat_id, "⚠️ Превышение общего лимита токенов")
                return False

            return True

        except Exception as ex:
            logger.exception(ex)
            await self.ws_manager.send_message_to_connection(chat_id, "⚠️ Ошибка сервиса")
            return False

    async def proceed_user_message(self, chat_id: UUID, message: str) -> bool:
        """
        Обработка сообщения пользователя
        """

        if not await self._check_limits(chat_id, message):
            return False

        asyncio.create_task(self.background_task(chat_id, message))

        return True

    @classmethod
    def _sanitize_string_optimized(cls, text: str) -> str:
        """
        Очистка строки от потенциально опасных символов для подачи в LLM
        """

        if not text:
            return ""

        allowed_categories = {"L", "N", "P", "Z", "S"}
        excluded_categories = {"So", "Sk", "Sm", "Sc"}

        result_chars = []
        append = result_chars.append

        for char in text:
            cat = unicodedata.category(char)
            if (cat[0] in allowed_categories and
                    cat not in excluded_categories):
                append(char)
            elif char in " \t\n\r.,!?:;-_()[]{}@#$%&*+=/\\|<>\"'`~^":
                append(char)
            else:
                append(" ")

        result = "".join(result_chars)
        return cls.REGEX.sub(" ", result).strip()

    async def _get_llm_answer(self, chat_id: UUID, message: str, chunks: str | None = None) -> SGigaChatAnswer:
        """
        Получение ответа от LLM
        """

        # загрузка истории сообщений
        intent = MessageIntent.intent_project if chunks else MessageIntent.intent_ontopic
        history = await self.get_history_for_api(chat_id, str(intent))

        # очистка сообщения пользователя от потенциально опасных символов
        cleaned_message = self._sanitize_string_optimized(message)

        # запрос к LLM
        async with gigachat_api as chatbot:
            giga_chat_answer: SGigaChatAnswer = await chatbot.send_message_to_llm(cleaned_message, history, chunks)

        return giga_chat_answer

    @staticmethod
    async def _get_answer_intent(answer: str) -> str:
        """
        Определение intent
        """

        # поиск команды intent_* от LLM
        pattern = r"\bintent_\w+"
        pattern_match = re.search(pattern, answer, re.IGNORECASE)

        return pattern_match.group(0)[:24].strip() if pattern_match else MessageIntent.intent_ontopic

    async def _get_ragbot_answer(self, chat_id: UUID, message: str) -> str:
        """
        Формирование ответа RAG-бота
        """

        # поиск ближайших чанков
        async with es_manager as es, vectorizer_manager as vectorizer:
            chunks = await RagBotService(es, vectorizer).get_top_chunks_list(message)

        # TODO: сделать обработку chunks is None
        chunks = "\n\n".join(chunks)

        # запрос к LLM
        giga_chat_answer = await self._get_llm_answer(chat_id, message, chunks=chunks)

        return giga_chat_answer.answer

    async def background_task(self, chat_id: UUID, message: str) -> None:
        """
        Фоновая отправка сообщения в LLM и обработка результата
        """

        try:
            # ответ от LLM
            giga_chat_answer = await self._get_llm_answer(chat_id, message)
            answer = giga_chat_answer.answer

            # определение intent
            intent = await self._get_answer_intent(answer)

            if intent == MessageIntent.intent_ontopic:
                # вопрос пользователя по теме авиации, выдаётся прямой ответ
                pass

            elif intent == MessageIntent.intent_project:
                # вопрос по теме проекта, ответ обрабатывает логика RAG-бота
                giga_chat_answer.answer = await self._get_ragbot_answer(chat_id, message)

            elif intent == MessageIntent.intent_feedback:
                # вопрос по теме обратной связи
                settings = await self.bot_settings.get_settings()
                giga_chat_answer.answer = settings.feedback

            else:
                # вопрос не по теме авиации, формируется шаблонный ответ
                giga_chat_answer.answer = self.intent_mapper.get(intent, MessageIntent.intent_offtopic)

            if not giga_chat_answer.answer:
                logger.warning("Пустой ответ для передачи пользователю")
                giga_chat_answer.answer = "⚠️ Ошибка сервиса"

            # отметка вопроса, ответа, темы и токенов в базе
            await self.db.chatbot.history.insert_one(
                data=giga_chat_answer,
                chat_id=chat_id,
                message=message,
                intent=intent,
                commit=True
            )

            # отправка ответа через websocket
            await self.ws_manager.send_message_to_connection(chat_id, giga_chat_answer.answer)

        except Exception as ex:
            logger.exception(ex)
            await self.db.rollback()
            await self.ws_manager.send_message_to_connection(chat_id, "⚠️ Ошибка сервиса")

        return None
