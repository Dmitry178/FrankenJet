from fastapi import HTTPException
from starlette import status

from app.exceptions.base import BaseCustomException


class UserNotFoundEx(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"


class PasswordIncorrectEx(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь или пароль неверный"


class UserNotActiveEx(BaseCustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь заблокирован"


class UserExistsEx(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже создан"


class UserCreationErrorEx(BaseCustomException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка создания пользователя"


class RegistrationNotAllowedEx(BaseCustomException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Регистрация пользователя недоступна"


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
unauthorized_403 = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
