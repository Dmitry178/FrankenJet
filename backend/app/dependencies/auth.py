from fastapi import Depends
from typing import Annotated

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config_const import TOKEN_TYPE_ACCESS
from app.exceptions import TokenTypeErrorEx, AuthUserErrorEx
from app.services.auth import AuthTokenService

security = HTTPBearer()


async def get_auth_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Получение id текущего аутентифицированного пользователя из заголовков
    """

    try:
        # получение тела токена
        token_payload = AuthTokenService.decode_token(credentials.credentials)

        # проверка типа токена
        if token_payload.get("type") != TOKEN_TYPE_ACCESS:
            raise TokenTypeErrorEx

        return token_payload.get("id")

    except (ExpiredSignatureError, InvalidTokenError, TokenTypeErrorEx, Exception) as ex:
        raise AuthUserErrorEx from ex


UserIdDep = Annotated[int, Depends(get_auth_user_id)]
