from fastapi import APIRouter, Response, HTTPException

from app.dependencies.auth import UserIdDep
from app.dependencies.db import DDB
from app.exceptions import UserNotFoundEx, PasswordIncorrectEx, UserExistsEx
from app.schemas.auth import SLoginUser
from app.services.auth import AuthServices
from app.types import status_ok

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", summary="Аутентификация пользователя по email и паролю")
async def user_login(response: Response, data: SLoginUser, db: DDB):
    """
    Аутентификация пользователя
    """

    try:
        tokens = await AuthServices(db).login(data)
        response.set_cookie(key="access", value=tokens.access_token)
        response.set_cookie(key="refresh", value=tokens.refresh_token)

        return {**status_ok, "data": tokens.model_dump(exclude_none=True)}

    except (UserNotFoundEx, PasswordIncorrectEx) as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)


@auth_router.post("/logout", summary="Выход из аккаунта")
async def user_logout(response: Response):
    """
    Выход пользователя
    """

    try:
        response.delete_cookie(
            key="access_token",
            # secure=True,
            # httponly=True,
            # samesite="lax",
        )
        return status_ok

    except:  # noqa  # TODO: доработать
        pass

    return {"status": "error", "detail": "Ошибка удаления cookie"}  # TODO: доработать


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


@auth_router.get("/info", summary="Получение информации о пользователе")
async def get_user_info(user_id: UserIdDep, db: DDB):
    """
    Получение информации о текущем аутентифицированном пользователе
    """

    # TODO: обернуть в try/except
    user_info = await AuthServices(db).get_user_info(user_id)

    return {**status_ok, "data": user_info.model_dump(exclude_none=True)}
