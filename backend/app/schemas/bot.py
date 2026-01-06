from pydantic import BaseModel, Field, EmailStr
from uuid import UUID


class SBotNotification(BaseModel):
    """
    Схема для отправки уведомления в телеграм-бот
    """

    notification: str  # уведомление


class SBotAuthNotification(BaseModel):
    """
    Схема для отправки уведомления об аутентификации администратора в телеграм-бот
    """

    user_id: UUID = Field(..., alias="user-id")  # id пользователя
    user_name: str | None = Field(None, alias="user-name")  # имя пользователя
    email: str | EmailStr = Field(..., alias="email")  # email пользователя
    roles: list | None = Field(None, alias="roles")  # роли пользователя
    client_ip: str | None = Field(None, alias="client-ip")  # ip-адрес
    user_agent: str | None = Field(None, alias="user-agent")  # данные браузера

    model_config = {
        "populate_by_name": True
    }


class SBotModeration(BaseModel):
    """
    Схема для отправки комментария на модерацию в телеграм-бот
    """

    id: int  # id комментария
    comment: str  # текст комментария
