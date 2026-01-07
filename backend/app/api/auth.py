from fastapi import APIRouter, Body, Request
from starlette import status

from app.api.openapi_examples import login_example
from app.core.logs import logger
from app.dependencies.auth import DAuthUserId, DAuthToken
from app.dependencies.db import DDB
from app.dependencies.rmq import DRmq
from app.exceptions.api import http_error_500
from app.exceptions.auth import UserNotFoundEx, PasswordIncorrectEx, UserExistsEx, TokenTypeErrorEx, TokenInvalidEx, \
    UserCreationErrorEx
from app.schemas.api import SuccessResponse
from app.schemas.auth import SLoginUser
from app.services.auth import AuthServices
from app.services.users import UsersServices
from app.types import status_ok

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/login",
    summary="Аутентификация по email и паролю",
)
async def user_login(
        db: DDB,
        rmq: DRmq,
        request: Request,
        data: SLoginUser = Body(openapi_examples=login_example)
):
    """
    Аутентификация пользователя по email и паролю
    """

    try:
        result = await AuthServices(db, rmq).login(data, request)
        return {**status_ok, "data": result}

    except (UserNotFoundEx, PasswordIncorrectEx) as ex:
        return ex.json_response

    except Exception as ex:
        logger.exception(ex)
        return http_error_500


@auth_router.post(
    "/register",
    summary="Регистрация пользователя",
    status_code=status.HTTP_201_CREATED,
)
async def user_register(db: DDB, data: SLoginUser = Body(openapi_examples=login_example)):
    """
    Регистрация пользователя
    """

    try:
        await UsersServices(db).create_user_by_email(data)
        return SuccessResponse()

    except UserExistsEx as ex:
        return ex.json_response

    except UserCreationErrorEx as ex:
        return ex.json_response

    except Exception as ex:
        logger.exception(ex)
        return http_error_500


@auth_router.post(
    "/refresh",
    summary="Перевыпуск токенов",
    status_code=status.HTTP_201_CREATED,
)
async def refresh_tokens(refresh_token: DAuthToken, db: DDB):
    """
    Перевыпуск access и refresh токенов по refresh-токену
    """

    try:
        data = await AuthServices(db).refresh(refresh_token)
        return {**status_ok, "data": data}

    except (TokenInvalidEx, TokenTypeErrorEx, UserNotFoundEx) as ex:
        raise ex.http_exception

    except Exception as ex:
        logger.exception(ex)
        return http_error_500


@auth_router.get("/info", summary="Информация о пользователе")
async def get_user_info(user_id: DAuthUserId, db: DDB):
    """
    Получение информации о текущем аутентифицированном пользователе
    """

    try:
        data = await AuthServices(db).get_user_info(user_id)
        return {**status_ok, "data": data}

    except UserNotFoundEx as ex:
        return ex.json_response

    except Exception as ex:
        logger.exception(ex)
        return http_error_500
