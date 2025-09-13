from fastapi import APIRouter, Query, Depends
from uuid import UUID

from app.core.logs import logger
from app.dependencies.auth import get_auth_editor_id
from app.dependencies.db import DDB
from app.schemas.articles import SCountriesFilters, SDesignBureaus
from app.services.bureaus import BureausServices
from app.types import status_ok, status_error

bureaus_router = APIRouter(prefix="/articles", tags=["Articles"])


@bureaus_router.get("/bureaus", summary="Список бюро")
async def get_design_bureaus(
        db: DDB,
        country: str | None = Query(None, description="Фильтр по стране"),
):
    """
    Получить список конструкторских бюро
    """

    filters = SCountriesFilters(country=country)
    data = await BureausServices(db).get_design_bureaus(filters)

    return {**status_ok, "data": data}


@bureaus_router.post(
    "/bureaus",
    summary="Добавление бюро",
    dependencies=[Depends(get_auth_editor_id)],
)
async def add_design_bureau(data: SDesignBureaus, db: DDB):
    """
    Создание карточки дизайнерского бюро
    """

    try:
        result = BureausServices(db).add_design_bureau(data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return {**status_error}


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
        result = BureausServices(db).edit_design_bureau(bureaus_id, data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return {**status_error}


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
        result = BureausServices(db).edit_design_bureau(bureau_id, data, exclude_unset=True)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return {**status_error}


@bureaus_router.delete(
    "/bureaus/{bureau_id}",
    summary="Удаление бюро",
    dependencies=[Depends(get_auth_editor_id)],
)
async def delete_design_bureau(bureau_id: UUID, db: DDB):
    """
    Удаление карточки дизайнерского бюро
    """

    try:
        result = BureausServices(db).delete_design_bureau(bureau_id)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.error(ex)
        return {**status_error}
