from fastapi import APIRouter, Query, Depends
from uuid import UUID

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id
from app.dependencies.db import DDB
from app.schemas.aircraft import SCountriesFilters, SDesigners
from app.services.designers import DesignersServices
from app.types import status_ok, status_error

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

    except Exception as ex:
        logger.exception(ex)
        return status_error


@designers_router.post(
    "/designers",
    summary="Добавление конструктора",
    dependencies=[Depends(get_auth_editor_id)],
)
async def add_design_bureau(data: SDesigners, db: DDB):
    """
    Создание карточки конструктора
    """

    try:
        result = DesignersServices(db).add_designer(data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


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

    except Exception as ex:
        logger.exception(ex)
        return status_error


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

    except Exception as ex:
        logger.error(ex)
        return status_error


@designers_router.delete(
    "/designers/{designer_id}",
    summary="Удаление конструктора",
    dependencies=[Depends(get_auth_editor_id)],
)
async def delete_designer(designer_id: UUID, db: DDB):
    """
    Удаление карточки конструктора
    """

    try:
        result = DesignersServices(db).delete_designer(designer_id)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return status_error
