from fastapi import HTTPException


class BaseAuthException(Exception):
    detail = "Ошибка"
    status_code = 400

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args)


class EUserNotFound(BaseAuthException):
    detail = "Пользователь не найден"
    status_code = 404


class EPasswordIncorrect(BaseAuthException):
    detail = "Пароль пользователя неверный"
    status_code = 401


user_or_password_incorrect_ex = HTTPException(status_code=401, detail="Пользователь или пароль неверный")
