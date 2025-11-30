import enum
import uuid

from sqlalchemy import Integer, UUID, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.db.models.base import TimestampMixin
from app.db.types import bool_false, str_24, str_32, str_512, bool_true


class ChatBotSettings(Base):
    """
    Настройки чат-бота
    """

    __tablename__ = "settings"
    __table_args__ = {"schema": "chat_bot"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enabled: Mapped[bool_false]  # активирован ли чат-бот
    model: Mapped[str_32 | None]  # название LLM-модели
    scope: Mapped[str_32 | None]  # scope
    system_prompt: Mapped[str | None]  # общий системный промт
    messages_per_user: Mapped[int | None]  # количество сообщений на пользователя
    messages_per_day: Mapped[int | None]  # количество сообщений в день на всех пользователей


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


class ChatHistory(Base, TimestampMixin):
    """
    История чата
    """

    __tablename__ = "chat"
    __table_args__ = {"schema": "chat_bot"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))  # id чата
    message: Mapped[str_512]  # сообщение пользователя
    answer: Mapped[str | None]  # ответ LLM (или автоответ)
    intent: Mapped[str_24 | None] = mapped_column(Enum(MessageIntent, native_enum=False, length=16))  # тема сообщения
    prompt_tokens: Mapped[int | None]  # количество токенов промта
    completion_tokens: Mapped[int | None]  # количество токенов ответа модели
    total_tokens: Mapped[int | None]  # количество токенов всего
    precached_prompt_tokens: Mapped[int | None]  # количество токенов кэша (истории)
    is_active: Mapped[bool_true]  # запись активна
