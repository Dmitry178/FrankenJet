from fastapi import HTTPException
from starlette import status


class BaseArticlesException(Exception):
    detail = "Error"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, *args, **kwargs):  # noqa
        super().__init__(self.detail, *args)


class ArticleNotFoundEx(BaseArticlesException):
    detail = "Article not found"
    status_code = status.HTTP_404_NOT_FOUND


article_not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
