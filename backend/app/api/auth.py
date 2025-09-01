from fastapi import APIRouter, HTTPException
from starlette import status

from app.dependencies.auth import AuthUserIdDep, AuthTokenDep
from app.dependencies.db import DDB
from app.exceptions import UserNotFoundEx, PasswordIncorrectEx, UserExistsEx, TokenTypeErrorEx, TokenInvalidEx
from app.schemas.auth import SLoginUser
from app.services.auth import AuthServices
from app.types import status_ok

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", summary="Аутентификация пользователя по email и паролю")
async def user_login(data: SLoginUser, db: DDB):
    """
    Аутентификация пользователя
    """

    try:
        tokens = await AuthServices(db).login(data)
        return {**status_ok, "data": tokens.model_dump()}

    except (UserNotFoundEx, PasswordIncorrectEx) as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)


@auth_router.post("/register", summary="Регистрация пользователя")
async def user_register(data: SLoginUser, db: DDB):
    """
    Регистрация пользователя
    """

    try:
        await AuthServices(db).register_user(data)
        return status_ok

    except UserExistsEx as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)


@auth_router.post("/refresh", summary="Перевыпуск токенов")
async def refresh_tokens(refresh_token: AuthTokenDep, db: DDB):
    """
    Перевыпуск access и refresh токенов по refresh-токену
    """

    try:
        tokens = await AuthServices(db).refresh(refresh_token)
        return {**status_ok, "data": tokens.model_dump()}

    except (TokenInvalidEx, TokenTypeErrorEx, UserNotFoundEx) as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)

    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@auth_router.get("/info", summary="Получение информации о пользователе")
async def get_user_info(user_id: AuthUserIdDep, db: DDB):
    """
    Получение информации о текущем аутентифицированном пользователе
    """

    # TODO: обернуть в try/except
    user_info = await AuthServices(db).get_user_info(user_id)

    return {**status_ok, "data": user_info.model_dump()}
