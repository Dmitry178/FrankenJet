from pydantic import BaseModel, EmailStr


class SLoginUser(BaseModel):
    """
    Схема логина пользователя
    """

    email: EmailStr
    password: str


class SRegisterUser(BaseModel):
    """
    Схема регистрации пользователя
    """

    email: EmailStr
    hashed_password: str


class SAuthTokens(BaseModel):
    """
    Схема jwt-токенов пользователя
    """

    access_token: str
    refresh_token: str | None = None  # TODO: сделать обязательным после добавления refresh-токена


class SUserInfo(BaseModel):
    """
    Схема информации о пользователе
    """

    id: int
    email: EmailStr
