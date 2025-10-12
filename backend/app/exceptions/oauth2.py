from app.exceptions.base import BaseCustomException


class OAuth2ErrorEx(BaseCustomException):
    detail = "OAuth2 error"
