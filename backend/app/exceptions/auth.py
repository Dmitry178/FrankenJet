from fastapi import HTTPException
from starlette import status


class BaseAuthException(Exception):
    detail = "Error"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, *args, **kwargs):  # noqa
        super().__init__(self.detail, *args)


class UserNotFoundEx(BaseAuthException):
    detail = "User not found"
    status_code = status.HTTP_404_NOT_FOUND


class PasswordIncorrectEx(BaseAuthException):
    detail = "Password incorrect"
    status_code = status.HTTP_401_UNAUTHORIZED


class UserExistsEx(BaseAuthException):
    detail = "User already exists"
    status_code = status.HTTP_409_CONFLICT


class UserCreationErrorEx(BaseAuthException):
    detail = "User creation failed"


class TokenInvalidEx(BaseAuthException):
    detail = "Invalid token"
    status_code = status.HTTP_401_UNAUTHORIZED


class TokenTypeErrorEx(BaseAuthException):
    detail = "Token type error"
    status_code = status.HTTP_401_UNAUTHORIZED


class AuthUserErrorEx(BaseAuthException):
    detail = "Auth user error"
    status_code = status.HTTP_401_UNAUTHORIZED


class AuthRoleErrorEx(BaseAuthException):
    detail = "Auth role error"
    status_code = status.HTTP_403_FORBIDDEN


unauthorized_401 = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
