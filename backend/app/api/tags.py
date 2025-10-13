from fastapi import APIRouter, Depends
from starlette import status

from app.core.logs import logger
from app.dependencies.auth import get_auth_admin_id, get_auth_editor_id
from app.dependencies.db import DDB
from app.exceptions.base import BaseCustomException
from app.schemas.api import SuccessResponse
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
        return SuccessResponse()

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
async def add_tag(tag: str, db: DDB):
    """
    Добавление тега
    """

    try:
        result = TagsServices(db).add_tag(tag)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@tags_router.put(
    "",
    summary="Изменение тега",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_tag(old_value: str, new_value: str, db: DDB):
    """
    Редактирование тега (put)
    """

    try:
        result = TagsServices(db).edit_tag(old_value, new_value)
        return {**status_ok, "data": result}

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
        row_count = TagsServices(db).delete_tag(tag)
        return SuccessResponse(data={"rows": row_count})

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
