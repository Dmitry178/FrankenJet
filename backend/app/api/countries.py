from fastapi import APIRouter, Depends
from uuid import UUID

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id
from app.dependencies.db import DDB
from app.schemas.aircraft import SCountries
from app.services.countries import CountriesServices
from app.types import status_ok, status_error

countries_router = APIRouter(prefix="/aircraft", tags=["Aircraft"])


@countries_router.get("/countries", summary="Список стран")
async def get_countries(db: DDB):
    """
    Получение списка стран
    """

    try:
        data = await CountriesServices(db).get_countries()
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@countries_router.post(
    "/countries",
    summary="Добавление страны",
    dependencies=[Depends(get_auth_editor_id)],
)
async def add_country(data: SCountries, db: DDB):
    """
    Создание карточки страны
    """

    try:
        result = CountriesServices(db).add_country(data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@countries_router.put(
    "/countries/{country_id}",
    summary="Изменение страны",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_country_put(country_id: UUID, data: SCountries, db: DDB):
    """
    Редактирование карточки страны (put)
    """

    try:
        result = CountriesServices(db).edit_country(country_id, data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@countries_router.patch(
    "/countries/{country_id}",
    summary="Изменение страны",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_country_post(country_id: UUID, data: SCountries, db: DDB):
    """
    Редактирование карточки страны (patch)
    """

    try:
        result = CountriesServices(db).edit_country(country_id, data, exclude_unset=True)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@countries_router.delete(
    "/countries/{country_id}",
    summary="Удаление страны",
    dependencies=[Depends(get_auth_editor_id)],
)
async def delete_country(country_id: UUID, db: DDB):
    """
    Удаление карточки страны
    """

    try:
        result = CountriesServices(db).delete_country(country_id)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error
