from pydantic import BaseModel, Field
from uuid import UUID


class SChatHistory(BaseModel):
    """
    Схема истории чатов
    """

    chat_id: UUID = Field(..., description="ID чата")
    message: str = Field(..., description="Сообщение пользователя")
    answer: str = Field(None, description="Ответ LLM")
    intent: str = Field(None, description="Тема сообщения")
    prompt_tokens: int = Field(None, description="Количество токенов промта")
    completion_tokens: int = Field(None, description="Количество токенов ответа модели")
    total_tokens: int = Field(None, description="Количество токенов всего")
    precached_prompt_tokens: int = Field(None, description="Количество токенов кэша (истории)")


class SChatBotSettings(BaseModel):
    """
    Схема настроек чат-бота
    """

    enabled: bool | None = Field(None, description="Активирован ли чат-бот")
    model: str | None = Field(None, max_length=32, description="Название LLM-модели")
    scope: str | None = Field(None, max_length=32, description="Название scope")
    system_prompt: str | None = Field(None, description="Системный промт")
    messages_per_user: int | None = Field(None, description="Количество сообщений на пользователя в день")
    messages_per_day: int | None = Field(None, description="Количество сообщений в день на всех пользователей")
