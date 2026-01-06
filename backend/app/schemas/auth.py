from pydantic import BaseModel, EmailStr
from uuid import UUID


class SLoginUser(BaseModel):
    """
    Схема логина пользователя

    В проекте логином по умолчанию является email, однако
    для демонстрационных целей предусмотрен пользователь с логином "admin",
    который не соответствует формату email. Поэтому тип поля email может быть
    как строкой (str), так и EmailStr.
    """

    email: str | EmailStr
    password: str


class SRegisterUser(BaseModel):
    """
    Схема регистрации пользователя

    При регистрации новых пользователей логином обязательно должен быть
    корректный email адрес.
    """

    email: EmailStr
    hashed_password: str


class SAuthTokens(BaseModel):
    """
    Схема jwt-токенов пользователя
    """

    access_token: str
    refresh_token: str


class SAuthUserInfo(BaseModel):
    """
    Схема информации об аутентифицированном пользователе
    """

    id: UUID
    name: str | None = None
    email: EmailStr | str
    roles: list | None = None
