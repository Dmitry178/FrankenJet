from fastapi import HTTPException


class BaseAuthException(Exception):
    detail = "Ошибка"
    status_code = 400

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args)


class UserNotFoundEx(BaseAuthException):
    detail = "Пользователь не найден"
    status_code = 404


class PasswordIncorrectEx(BaseAuthException):
    detail = "Пароль пользователя неверный"
    status_code = 401


class UserExistsEx(BaseAuthException):
    detail = "Пользователь уже зарегистрирован"
    status_code = 409
