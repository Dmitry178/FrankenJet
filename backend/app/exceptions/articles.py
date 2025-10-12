from starlette import status

from app.exceptions.base import BaseCustomException


class ArticleNotFoundEx(BaseCustomException):
    detail = "Статья не найдена"
    status_code = status.HTTP_404_NOT_FOUND
