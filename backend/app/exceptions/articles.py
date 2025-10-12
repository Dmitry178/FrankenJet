from fastapi import HTTPException
from starlette import status

from app.exceptions.base import BaseCustomException


class ArticleNotFoundEx(BaseCustomException):
    detail = "Article not found"
    status_code = status.HTTP_404_NOT_FOUND


article_not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
