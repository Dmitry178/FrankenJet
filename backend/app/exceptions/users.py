from starlette import status

from app.exceptions.base import BaseCustomException


class FileNotImageEx(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Файл не является изображением"


class FileTooLargeEx(BaseCustomException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    detail = "Файл слишком большой"
