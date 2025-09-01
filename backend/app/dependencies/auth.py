from fastapi import Depends
from typing import Annotated

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config_const import TOKEN_TYPE_ACCESS
from app.exceptions import TokenTypeErrorEx, AuthUserErrorEx
from app.services.security import SecurityService

security = HTTPBearer()


async def get_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Получение токена из заголовков
    """

    return credentials.credentials


async def get_auth_user_id(token: str = Depends(get_auth_token)) -> int:
    """
    Получение id текущего аутентифицированного пользователя из access-токена в заголовках
    """

    try:
        token_payload = SecurityService.decode_token(token)

        # проверка типа токена
        if token_payload.get("type") != TOKEN_TYPE_ACCESS:
            raise TokenTypeErrorEx

        return token_payload.get("id")

    except (ExpiredSignatureError, InvalidTokenError, TokenTypeErrorEx, ValueError) as ex:
        raise AuthUserErrorEx from ex


AuthTokenDep = Annotated[str, Depends(get_auth_token)]
AuthUserIdDep = Annotated[int, Depends(get_auth_user_id)]
