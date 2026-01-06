import enum
import uuid

from sqlalchemy import Integer, UUID, Enum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.db.models.base import TimestampIdxMixin
from app.db.types import bool_false, str_24, str_32, str_128, str_512, bool_true, int_0


class ChatBotSettings(Base):
    """
    Настройки чат-бота
    """

    __tablename__ = "settings"
    __table_args__ = (
        CheckConstraint("id=1", name="settings_single_row_check"),
        {"schema": "chatbot"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enabled: Mapped[bool_false]  # активирован ли чат-бот
    model: Mapped[str_32 | None]  # название LLM-модели
    scope: Mapped[str_32 | None]  # scope
    system_prompt: Mapped[str | None]  # общий системный промт
    rag_prompt: Mapped[str | None]  # системный промт для RAG-бота
    feedback: Mapped[str_128 | None]  # текст ответа на вопрос по обратной связи
    user_daily_tokens: Mapped[int | None]  # количество токенов в день на пользователя
    total_daily_tokens: Mapped[int | None]  # количество токенов в день на всех пользователей


class MessageIntent(str, enum.Enum):
    """
    Тема сообщения
    """

    intent_greeting = "intent_greeting"  # приветствие
    intent_ontopic = "intent_ontopic"  # сообщение по теме авиации
    intent_offtopic = "intent_offtopic"  # сообщение не по теме
    intent_feedback = "intent_feedback"  # сообщение на тему обратной связи
    intent_project = "intent_project"  # сообщение по теме проекта
    intent_timeout = "intent_timeout"  # истекло время ожидания от LLM
    intent_blacklist = "intent_blacklist"  # сообщение заблокировано LLM
    intent_spam = "intent_spam"  # спамерское сообщение
    intent_unknown = "intent_unknown"  # нераспознанная тема

    def __str__(self) -> str:
        return self.value


class Chat(Base, TimestampIdxMixin):
    """
    История чата
    """

    __tablename__ = "chat"
    __table_args__ = {"schema": "chatbot"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))  # id чата
    message: Mapped[str_512]  # сообщение пользователя
    answer: Mapped[str | None]  # ответ LLM (или автоответ)
    intent: Mapped[str_24 | None] = mapped_column(Enum(MessageIntent, native_enum=False, length=24))  # тема сообщения
    prompt_tokens: Mapped[int | None]  # количество токенов промта
    completion_tokens: Mapped[int | None]  # количество токенов ответа модели
    total_tokens: Mapped[int_0]  # количество токенов всего
    precached_prompt_tokens: Mapped[int_0]  # количество токенов кэша (истории)
    is_active: Mapped[bool_true]  # запись активна
