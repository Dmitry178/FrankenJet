"""
Эндпоинты для работы с данными конструкторов. В данной итерации проекта не используются.
"""

from fastapi import APIRouter, Query, Depends
from starlette import status
from uuid import UUID

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id, get_auth_admin_id
from app.dependencies.db import DDB
from app.exceptions.base import BaseCustomException
from app.schemas.api import SuccessResponse
from app.schemas.countries import SCountriesFilters
from app.schemas.designers import SDesigners
from app.services.designers import DesignersServices
from app.types import status_ok

designers_router = APIRouter(prefix="/aircraft", tags=["Aircraft"])


@designers_router.get("/designers", summary="Список конструкторов")
async def get_designers(
        db: DDB,
        country: str | None = Query(None, description="Фильтр по стране"),
):
    """
    Получить список конструкторов
    """

    try:
        filters = SCountriesFilters(country=country)
        data = await DesignersServices(db).get_designers(filters)
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@designers_router.post(
    "/designers",
    summary="Добавление конструктора",
    dependencies=[Depends(get_auth_editor_id)],
    status_code=status.HTTP_201_CREATED,
)
async def add_design_bureau(data: SDesigners, db: DDB):
    """
    Создание карточки конструктора
    """

    try:
        result = DesignersServices(db).add_designer(data)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@designers_router.put(
    "/designers/{designer_id}",
    summary="Изменение конструктора",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_designer_put(designer_id: UUID, data: SDesigners, db: DDB):
    """
    Редактирование карточки конструктора (put)
    """

    try:
        result = DesignersServices(db).edit_designer(designer_id, data)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@designers_router.patch(
    "/designers/{designer_id}",
    summary="Изменение конструктора",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_designer_post(designer_id: UUID, data: SDesigners, db: DDB):
    """
    Редактирование карточки конструктора (patch)
    """

    try:
        result = DesignersServices(db).edit_designer(designer_id, data, exclude_unset=True)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@designers_router.delete(
    "/designers/{designer_id}",
    summary="Удаление конструктора",
    dependencies=[Depends(get_auth_admin_id)],
)
async def delete_designer(designer_id: UUID, db: DDB):
    """
    Удаление карточки конструктора
    """

    try:
        row_count = DesignersServices(db).delete_designer(designer_id)
        return SuccessResponse(data={"rows": row_count})

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
