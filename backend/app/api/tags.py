from fastapi import APIRouter, Depends, Body
from starlette import status

from app.core.logs import logger
from app.dependencies.auth import get_auth_admin_id, get_auth_editor_id
from app.dependencies.db import DDB
from app.exceptions.api import record_was_not_found_404
from app.exceptions.base import BaseCustomException
from app.schemas.api import SuccessResponse
from app.schemas.tags import STagsPut
from app.services.tags import TagsServices
from app.types import status_ok

tags_router = APIRouter(prefix="/tags", tags=["Tags"])


@tags_router.post(
    "/generate",
    summary="Автоматическое создание",
    dependencies=[Depends(get_auth_admin_id)],
    status_code=status.HTTP_201_CREATED,
)
async def create_tags(db: DDB):
    """
    Автоматическое создание тегов
    """

    try:
        await TagsServices(db).auto_create()
        return {**status_ok}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@tags_router.get("", summary="Список тегов")
async def get_tags(db: DDB):
    """
    Получение списка тегов
    """

    try:
        data = await TagsServices(db).get_tags()
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@tags_router.post(
    "",
    summary="Добавление тега",
    dependencies=[Depends(get_auth_editor_id)],
    status_code=status.HTTP_201_CREATED,
)
async def add_tag(
        db: DDB,
        tag: str = Body(..., embed=True, max_length=32),
):
    """
    Добавление тега
    """

    try:
        result = await TagsServices(db).add_tag(tag)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@tags_router.put(
    "",
    summary="Изменение тега",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_tag(db: DDB, data: STagsPut):
    """
    Редактирование тега (put)
    """

    try:
        result = await TagsServices(db).edit_tag(data.old_value, data.new_value)
        return {**status_ok, "data": result} if result else record_was_not_found_404

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@tags_router.delete(
    "/{tag}",
    summary="Удаление тега",
    dependencies=[Depends(get_auth_admin_id)],
)
async def delete_tag(tag: str, db: DDB):
    """
    Удаление тега
    """

    try:
        row_count = await TagsServices(db).delete_tag(tag)
        return SuccessResponse(data={"rows": row_count})

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
