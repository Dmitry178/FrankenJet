from fastapi import APIRouter, Depends, Query, UploadFile, File
from uuid import UUID

from app.config.app import MAX_IMAGE_FILE_SIZE, ALLOWED_IMAGE_TYPES
from app.core.logs import logger
from app.dependencies.auth import get_auth_user_id, get_auth_admin_id
from app.dependencies.db import DDB
from app.dependencies.s3 import DS3
from app.exceptions.api import record_was_not_found_404
from app.exceptions.auth import UserNotFoundEx
from app.exceptions.base import BaseCustomException
from app.exceptions.users import FileNotImageEx, FileTooLargeEx
from app.schemas.api import SuccessResponse
from app.schemas.users import SEditUserProfile
from app.services.users import UsersServices
from app.types import status_ok

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/profile", summary="Получить данные пользователя")
async def get_profile(db: DDB, user_id: UUID = Depends(get_auth_user_id)):
    """
    Получение данных профиля пользователя
    """

    try:
        result = await UsersServices(db).get_user_profile(user_id)
        return SuccessResponse(data=result)

    except UserNotFoundEx as ex:
        return ex.json_response

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@users_router.put("/profile", summary="Обновить данные пользователя")
async def edit_profile(db: DDB, data: SEditUserProfile, user_id: UUID = Depends(get_auth_user_id)):
    """
    Обновление данных профиля пользователя
    """

    try:
        result = await UsersServices(db).edit_user_profile(user_id, data)
        return SuccessResponse(data=result) if result else record_was_not_found_404

    except UserNotFoundEx as ex:
        return ex.json_response

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@users_router.get("", summary="Список пользователей", dependencies=[Depends(get_auth_admin_id)])
async def get_users(
        db: DDB,
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
):
    """
    Получение списка пользователей (admin only)
    """

    try:
        data = await UsersServices(db).get_paginated_users(page, page_size)
        return SuccessResponse(data=data)

    except UserNotFoundEx as ex:
        return ex.json_response

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@users_router.post("/avatar")
async def upload_avatar(
        db: DDB,
        s3: DS3,
        avatar: UploadFile = File(...),
        user_id: UUID = Depends(get_auth_user_id)
):
    """
    Загрузка аватара пользователя
    """

    try:
        # валидация типа файла
        content_type = avatar.content_type.lower()
        if content_type not in ALLOWED_IMAGE_TYPES:  # .startswith("image/")
            raise FileNotImageEx

        # чтение содержимого файла
        content: bytes = await avatar.read()

        # проверка ограничения размера файла
        if len(content) > MAX_IMAGE_FILE_SIZE:
            raise FileTooLargeEx

        # загрузка файла в S3
        data = await UsersServices(db, s3).load_avatar(user_id, content, content_type)

        return SuccessResponse(data=data)

    except (FileNotImageEx, FileTooLargeEx) as ex:
        return ex.json_response

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@users_router.delete("/avatar")
async def remove_avatar(
        db: DDB,
        user_id: UUID = Depends(get_auth_user_id)
):
    """
    Удаление аватара пользователя
    """

    try:
        await UsersServices(db).delete_avatar(user_id)
        return status_ok

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
