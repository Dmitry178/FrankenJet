from fastapi import APIRouter, Response

from app.db.deps import DDB
from app.exceptions import EUserNotFound, EPasswordIncorrect, user_or_password_incorrect_ex
from app.schemas.auth import SUserLogin
from app.services.auth import AuthServices
from app.types import status_ok

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", summary="Аутентификация пользователя по email и паролю")
async def user_login(response: Response, data: SUserLogin, db: DDB):
    """
    Аутентификация пользователя
    """

    try:
        access_token = await AuthServices(db).login(data)
        response.set_cookie(key="access_token", value=access_token)
        return access_token

    except (EUserNotFound, EPasswordIncorrect) as ex:
        raise user_or_password_incorrect_ex


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
async def user_register(db: DDB):
    """
    Регистрация пользователя
    """

    return {"status": "coming soon"}


@auth_router.get("/info", summary="Получение информации о пользователе")
async def user_info(db: DDB):
    """
    Получение информации об аутентифицированном пользователе
    """

    return {"status": "coming soon"}
