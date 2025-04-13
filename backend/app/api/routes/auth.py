from fastapi import APIRouter

from app.api.deps import DBDep

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", summary="Вход в аккаунт")
async def user_login(db: DBDep):
    """
    Логин пользователя
    """

    return {"status": "coming soon"}


@auth_router.post("/logout", summary="Выход из аккаунта")
async def user_logout():
    """
    Выход пользователя
    """

    return {"status": "coming soon"}


@auth_router.post("/register", summary="Регистрация пользователя")
async def user_register(db: DBDep):
    """
    Регистрация пользователя
    """

    return {"status": "coming soon"}


@auth_router.get("/info", summary="Получение информации о пользователе")
async def user_info(db: DBDep):
    """
    Получение информации об аутентифицированном пользователе
    """

    return {"status": "coming soon"}
