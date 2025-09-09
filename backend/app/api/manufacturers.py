from fastapi import APIRouter, Query, Depends
from uuid import UUID

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id
from app.dependencies.db import DDB
from app.schemas.articles import SCountriesFilters, SManufacturers
from app.services.manufacturers import ManufacturersServices
from app.types import status_ok, status_error

manufacturers_router = APIRouter(prefix="/articles", tags=["Articles"])


@manufacturers_router.get("/manufacturers", summary="Список производителей")
async def get_manufacturers(
        db: DDB,
        country: str | None = Query(None, description="Фильтр по стране"),
):
    """
    Получить список производителей
    """

    filters = SCountriesFilters(country=country)
    data = await ManufacturersServices(db).get_manufacturers(filters)

    return {**status_ok, "data": data}


@manufacturers_router.post(
    "/manufacturers",
    summary="Добавление производителя",
    dependencies=[Depends(get_auth_editor_id)],
)
async def add_manufacturer(data: SManufacturers, db: DDB):
    """
    Создание карточки производителя
    """

    try:
        result = ManufacturersServices(db).add_manufacturer(data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return {**status_error}


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
        result = ManufacturersServices(db).edit_manufacturer(manufacturer_id, data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return {**status_error}


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
        result = ManufacturersServices(db).edit_manufacturer(manufacturer_id, data, exclude_unset=True)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return {**status_error}


@manufacturers_router.delete(
    "/manufacturers/{manufacturer_id}",
    summary="Удаление производителя",
    dependencies=[Depends(get_auth_editor_id)],
)
async def delete_manufacturer(manufacturer_id: UUID, db: DDB):
    """
    Удаление карточки производителя
    """

    try:
        result = ManufacturersServices(db).delete_manufacturer(manufacturer_id)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return {**status_error}
