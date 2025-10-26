"""
Эндпоинты для работы с данными производителей. В данной итерации проекта не используются.
"""

from fastapi import APIRouter, Query, Depends
from starlette import status
from uuid import UUID

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id, get_auth_admin_id
from app.dependencies.db import DDB
from app.exceptions.api import record_was_not_found_404
from app.exceptions.base import BaseCustomException
from app.schemas.api import SuccessResponse
from app.schemas.countries import SCountriesFilters
from app.schemas.manufacturers import SManufacturers
from app.services.manufacturers import ManufacturersServices
from app.types import status_ok

manufacturers_router = APIRouter(prefix="/aircraft", tags=["Aircraft"])


@manufacturers_router.get("/manufacturers", summary="Список производителей")
async def get_manufacturers(
        db: DDB,
        country: str | None = Query(None, description="Фильтр по стране"),
):
    """
    Получить список производителей
    """

    try:
        filters = SCountriesFilters(country=country)
        data = await ManufacturersServices(db).get_manufacturers(filters)
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@manufacturers_router.post(
    "/manufacturers",
    summary="Добавление производителя",
    dependencies=[Depends(get_auth_editor_id)],
    status_code=status.HTTP_201_CREATED,
)
async def add_manufacturer(data: SManufacturers, db: DDB):
    """
    Создание карточки производителя
    """

    try:
        result = await ManufacturersServices(db).add_manufacturer(data)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@manufacturers_router.put(
    "/manufacturers/{manufacturer_id}",
    summary="Изменение производителя",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_manufacturer_put(manufacturer_id: UUID, data: SManufacturers, db: DDB):
    """
    Редактирование карточки производителя (put)
    """

    try:
        result = await ManufacturersServices(db).edit_manufacturer(manufacturer_id, data)
        return {**status_ok, "data": result} if result else record_was_not_found_404

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@manufacturers_router.patch(
    "/manufacturers/{manufacturer_id}",
    summary="Изменение производителя",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_manufacturer_post(manufacturer_id: UUID, data: SManufacturers, db: DDB):
    """
    Редактирование карточки производителя (patch)
    """

    try:
        result = await ManufacturersServices(db).edit_manufacturer(manufacturer_id, data, exclude_unset=True)
        return {**status_ok, "data": result} if result else record_was_not_found_404

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@manufacturers_router.delete(
    "/manufacturers/{manufacturer_id}",
    summary="Удаление производителя",
    dependencies=[Depends(get_auth_admin_id)],
)
async def delete_manufacturer(manufacturer_id: UUID, db: DDB):
    """
    Удаление карточки производителя
    """

    try:
        row_count = await ManufacturersServices(db).delete_manufacturer(manufacturer_id)
        return SuccessResponse(data={"rows": row_count})

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
