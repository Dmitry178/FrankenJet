from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID


class SUserInfo(BaseModel):
    """
    Схема информации о пользователе
    """

    # дублирование кода в схемах оставлено для наглядности

    id: UUID
    email: EmailStr
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None


class SUserCreateOAuth2(BaseModel):
    """
    Схема создания пользователя через OAuth2
    """

    # дублирование кода в схемах оставлено для наглядности

    email: EmailStr
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None


class SUserCreateEmail(BaseModel):
    """
    Схема создания пользователя с использованием email
    """

    email: EmailStr
    hashed_password: str


class SUserProfile(BaseModel):
    """
    Схема данных профиля пользователя
    """

    # дублирование кода в схемах оставлено для наглядности

    id: UUID
    email: str
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None
    roles: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class SEditUserProfile(BaseModel):
    """
    Схема для редактирования данных профиля пользователя
    """

    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
