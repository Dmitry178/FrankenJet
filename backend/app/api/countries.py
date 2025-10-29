from fastapi import APIRouter, Depends, Path, Body
from starlette import status

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id, get_auth_admin_id
from app.dependencies.db import DDB
from app.exceptions.api import record_was_not_found_404
from app.exceptions.base import BaseCustomException
from app.schemas.api import SuccessResponse
from app.schemas.countries import SCountries
from app.services.countries import CountriesServices
from app.types import status_ok

countries_router = APIRouter(prefix="/countries", tags=["Countries"])


@countries_router.get("", summary="Список стран")
async def get_countries(db: DDB):
    """
    Получение списка стран
    """

    try:
        data = await CountriesServices(db).get_countries()
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.error(ex)
        return ex.json_response


@countries_router.post(
    "",
    summary="Добавление страны",
    dependencies=[Depends(get_auth_editor_id)],
    status_code=status.HTTP_201_CREATED,
)
async def add_country(db: DDB, data: SCountries = Body(...)):
    """
    Создание карточки страны
    """

    try:
        result = await CountriesServices(db).add_country(data)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.error(ex)
        return ex.json_response


@countries_router.put(
    "/{country_id}",
    summary="Изменение страны",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_country_put(
        db: DDB,
        country_id: str = Path(...),
        data: SCountries = Body(...)
):
    """
    Редактирование карточки страны (put)
    """

    try:
        result = await CountriesServices(db).edit_country(country_id, data)
        return {**status_ok, "data": result} if result else record_was_not_found_404

    except BaseCustomException as ex:
        logger.error(ex)
        return ex.json_response


@countries_router.patch(
    "/{country_id}",
    summary="Изменение страны",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_country_post(
        db: DDB,
        country_id: str = Path(...),
        data: SCountries = Body(...)
):
    """
    Редактирование карточки страны (patch)
    """

    try:
        result = await CountriesServices(db).edit_country(country_id, data, exclude_unset=True)
        return {**status_ok, "data": result} if result else record_was_not_found_404

    except BaseCustomException as ex:
        logger.error(ex)
        return ex.json_response


@countries_router.delete(
    "/{country_id}",
    summary="Удаление страны",
    dependencies=[Depends(get_auth_admin_id)],  # удалять страны может только админ
)
async def delete_country(db: DDB, country_id: str = Path(...)):
    """
    Удаление карточки страны
    """

    try:
        row_count = await CountriesServices(db).delete_country(country_id)
        return SuccessResponse(data={"rows": row_count})

    except BaseCustomException as ex:
        logger.error(ex)
        return ex.json_response
