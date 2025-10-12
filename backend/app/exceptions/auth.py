from fastapi import HTTPException
from starlette import status

from app.exceptions.base import BaseCustomException


class UserNotFoundEx(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь или пароль неверный"


class PasswordIncorrectEx(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь или пароль неверный"


class UserExistsEx(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже создан"


class UserCreationErrorEx(BaseCustomException):
    detail = "Ошибка создания пользователя"


class TokenInvalidEx(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Ошибка токена"


class TokenTypeErrorEx(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Ошибка типа токена"


class AuthUserErrorEx(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Ошибка аутентификации"


class AuthRoleErrorEx(BaseCustomException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Ошибка авторизации"


unauthorized_401 = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
