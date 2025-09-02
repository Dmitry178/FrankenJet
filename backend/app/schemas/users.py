from pydantic import BaseModel, EmailStr


class SUserInfo(BaseModel):
    """
    Схема информации о пользователе
    """

    # TODO: убрать дублирование кода в схемах (пока оставлено для наглядности)

    id: int
    email: EmailStr
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None


class SUserCreateOAuth2(BaseModel):
    """
    Схема создания пользователя через OAuth2
    """

    # TODO: убрать дублирование кода в схемах (пока оставлено для наглядности)

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
