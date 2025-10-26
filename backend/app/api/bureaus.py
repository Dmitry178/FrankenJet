"""
Эндпоинты для работы с данными конструкторских бюро. В данной итерации проекта не используются.
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
from app.schemas.bureaus import SDesignBureaus
from app.schemas.countries import SCountriesFilters
from app.services.bureaus import BureausServices
from app.types import status_ok

bureaus_router = APIRouter(prefix="/aircraft", tags=["Aircraft"])


@bureaus_router.get("/bureaus", summary="Список бюро")
async def get_design_bureaus(
        db: DDB,
        country: str | None = Query(None, description="Фильтр по стране"),
):
    """
    Получить список конструкторских бюро
    """

    try:
        filters = SCountriesFilters(country=country)
        data = await BureausServices(db).get_design_bureaus(filters)
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@bureaus_router.post(
    "/bureaus",
    summary="Добавление бюро",
    dependencies=[Depends(get_auth_editor_id)],
    status_code=status.HTTP_201_CREATED,
)
async def add_design_bureau(data: SDesignBureaus, db: DDB):
    """
    Создание карточки дизайнерского бюро
    """

    try:
        result = await BureausServices(db).add_design_bureau(data)
        return {**status_ok, "data": result}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@bureaus_router.put(
    "/bureaus/{bureau_id}",
    summary="Изменение бюро",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_design_bureau_put(bureaus_id: UUID, data: SDesignBureaus, db: DDB):
    """
    Редактирование карточки дизайнерского бюро (put)
    """

    try:
        result = await BureausServices(db).edit_design_bureau(bureaus_id, data)
        return {**status_ok, "data": result} if result else record_was_not_found_404

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@bureaus_router.patch(
    "/bureaus/{bureau_id}",
    summary="Изменение бюро",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_design_bureau_post(bureau_id: UUID, data: SDesignBureaus, db: DDB):
    """
    Редактирование карточки дизайнерского бюро (patch)
    """

    try:
        result = await BureausServices(db).edit_design_bureau(bureau_id, data, exclude_unset=True)
        return {**status_ok, "data": result} if result else record_was_not_found_404

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@bureaus_router.delete(
    "/bureaus/{bureau_id}",
    summary="Удаление бюро",
    dependencies=[Depends(get_auth_admin_id)],
)
async def delete_design_bureau(bureau_id: UUID, db: DDB):
    """
    Удаление карточки дизайнерского бюро
    """

    try:
        row_count = await BureausServices(db).delete_design_bureau(bureau_id)
        return SuccessResponse(data={"rows": row_count})

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
