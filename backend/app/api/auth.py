from fastapi import APIRouter, HTTPException, Body
from starlette import status

from app.api.responses import login_example
from app.core.logs import logger
from app.dependencies.auth import DAuthUserId, DAuthToken
from app.dependencies.db import DDB
from app.exceptions.auth import UserNotFoundEx, PasswordIncorrectEx, UserExistsEx, TokenTypeErrorEx, TokenInvalidEx, \
    UserCreationErrorEx
from app.schemas.auth import SLoginUser
from app.services.auth import AuthServices
from app.services.users import UsersServices
from app.types import status_ok

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", summary="Аутентификация пользователя по email и паролю")
async def user_login(db: DDB, data: SLoginUser = Body(openapi_examples=login_example)):
    """
    Аутентификация пользователя
    """

    try:
        result = await AuthServices(db).login(data)
        return {**status_ok, "data": result}

    except (UserNotFoundEx, PasswordIncorrectEx) as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)

    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@auth_router.post("/register", summary="Регистрация пользователя")
async def user_register(db: DDB, data: SLoginUser = Body(openapi_examples=login_example)):
    """
    Регистрация пользователя
    """

    try:
        await UsersServices(db).create_user_by_email(data)
        return status_ok

    except (UserCreationErrorEx, UserExistsEx) as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)

    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@auth_router.post("/refresh", summary="Перевыпуск токенов")
async def refresh_tokens(refresh_token: DAuthToken, db: DDB):
    """
    Перевыпуск access и refresh токенов по refresh-токену
    """

    try:
        result = await AuthServices(db).refresh(refresh_token)
        return {**status_ok, "data": result}

    except (TokenInvalidEx, TokenTypeErrorEx, UserNotFoundEx) as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)

    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@auth_router.get("/info", summary="Информация о пользователе")
async def get_user_info(user_id: DAuthUserId, db: DDB):
    """
    Получение информации о текущем аутентифицированном пользователе
    """

    try:
        user_info = await AuthServices(db).get_user_info(user_id)
        return {**status_ok, "data": user_info}

    except UserNotFoundEx:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    except Exception as ex:
        logger.error(ex)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
