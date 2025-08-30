from fastapi import Depends, HTTPException, Request
from typing import Annotated

from app.services.auth import AuthTokenService


def get_auth_user_id(request: Request) -> int:
    """
    Получение id текущего аутентифицированного пользователя из cookies
    """

    access_token = request.cookies.get("access_token", None)
    if not access_token:
        raise HTTPException(status_code=401, detail="Token not found")

    decoded_token = AuthTokenService().decode_token(access_token)
    if not decoded_token:
        raise HTTPException(status_code=401, detail="Token error")

    user_id = decoded_token.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")

    return user_id


UserIdDep = Annotated[int, Depends(get_auth_user_id)]
