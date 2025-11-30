import asyncio
import re
import unicodedata

from uuid import UUID

from app.config.app import GIGACHAT_USER_MESSAGE_MAX_SIZE
from app.core.db_manager import DBManager
from app.core.gigachat import gigachat_api
from app.core.ws_manager import WSBotManager
from app.db.models.chat_bot import MessageIntent
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.gigachat import SGigaChatAnswer
from scripts.init_db import logger


class ChatBotServices:

    db: DBManager | None

    intent_mapper = {
        str(MessageIntent.intent_greeting): "Приветствую. Вы можете задать вопрос по теме авиации.",
        str(MessageIntent.intent_offtopic): "Я могу отвечать только по теме авиации.",
        str(MessageIntent.intent_feedback): "Функция ответа на этот вопрос в процессе разработки.",
        str(MessageIntent.intent_project): "Функция ответа на этот вопрос в процессе разработки.",
        str(MessageIntent.intent_timeout): "⚠️ Превышено время ожидания ответа от сервера.",
        str(MessageIntent.intent_blacklist): "Я могу отвечать только по теме авиации.",
        str(MessageIntent.intent_spam): "Я могу отвечать только по теме авиации.",
    }

    REGEX = re.compile(r'\s+')

    def __init__(self, db: DBManager | None = None, ws_manager: WSBotManager | None = None) -> None:
        self.ws_manager = ws_manager
        self.db = db

    @handle_basic_db_errors
    async def get_history_for_bot(self, chat_id: UUID) -> list:
        """
        Получение истории чата пользователя для отправки на frontend
        """

        result = await self.db.chatbot.history.get_user_history(chat_id, api=False)
        return result[::-1]

    @handle_basic_db_errors
    async def get_history_for_api(self, chat_id: UUID) -> list:
        """
        Получение истории чата пользователя для отправки в LLM по API
        """

        history = []
        raw_history = await self.db.chatbot.history.get_user_history(chat_id, api=True, limit=4)

        for item in raw_history[::-1]:
            if message := item.get("message"):
                history.append({"role": "user", "content": message})
            if answer := item.get("answer"):
                history.append({"role": "assistant", "content": answer})

        return history

    @handle_basic_db_errors
    async def proceed_user_message(self, chat_id: UUID, message: str) -> bool | None:
        """
        Обработка сообщения пользователя
        """

        if not message:
            return

        if len(message) > GIGACHAT_USER_MESSAGE_MAX_SIZE:
            await self.ws_manager.send_message_to_chat(
                chat_id,
                f"⚠️ Превышение максимальной длины сообщения в {GIGACHAT_USER_MESSAGE_MAX_SIZE} символов"
            )
            return False

        asyncio.create_task(self.background_task(chat_id, message))

        return True

    @classmethod
    def sanitize_string_optimized(cls, text: str) -> str:
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

    async def background_task(self, chat_id: UUID, message: str) -> None:
        """
        Фоновая отправка сообщения в LLM и обработка результата
        """

        try:
            history = await self.get_history_for_api(chat_id)

            async with gigachat_api as chatbot:
                cleaned_message = self.sanitize_string_optimized(message)
                giga_chat_answer: SGigaChatAnswer = await chatbot.send_message(cleaned_message, history)

            answer = giga_chat_answer.answer

            # поиск команды intent_* от LLM
            pattern = r"\bintent_\w+"
            match = re.search(pattern, answer, re.IGNORECASE)

            if match:
                # вопрос пользователя не по теме авиации, формируем ответ
                intent = match.group(0)[:24]
                giga_chat_answer.answer = self.intent_mapper.get(intent, MessageIntent.intent_offtopic)
            else:
                # вопрос пользователя по теме авиации, выдаём прямой ответ
                intent = MessageIntent.intent_ontopic

            # отметка вопроса, ответа, темы и токенов в базе
            await self.db.chatbot.history.insert_one(
                data=giga_chat_answer,
                chat_id=chat_id,
                message=message,
                intent=intent,
                commit=True
            )

            # отправка ответа через websocket
            await self.ws_manager.send_message_to_chat(chat_id, giga_chat_answer.answer)

        except Exception as ex:
            logger.error(ex)
            await self.db.rollback()
            await self.ws_manager.send_message_to_chat(chat_id, "⚠️ Ошибка сервиса")

        return None
