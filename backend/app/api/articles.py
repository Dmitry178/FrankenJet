from fastapi import APIRouter, Query

from app.core.logs import logger
from app.dependencies.db import DDB
from app.schemas.aircraft import SCountriesFilters
from app.services.articles import ArticlesServices
from app.types import status_ok

articles_router = APIRouter(prefix="/articles", tags=["Articles"])


@articles_router.get("/countries", summary="Список стран")
async def get_countries(db: DDB):
    """
    Получить список стран
    """

    try:
        data = await ArticlesServices(db).get_countries()
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)


@articles_router.get("/bureaus", summary="Список конструкторских бюро")
async def get_design_bureaus(
        db: DDB,
        country: str | None = Query(None, description="Фильтр по стране"),
):
    """
    Получить список конструкторских бюро
    """

    filters = SCountriesFilters(country=country)
    data = await ArticlesServices(db).get_design_bureaus(filters)

    return {**status_ok, "data": data}


@articles_router.get("/designers", summary="Список конструкторов")
async def get_designers(
        db: DDB,
        country: str | None = Query(None, description="Фильтр по стране"),
):
    """
    Получить список конструкторов
    """

    filters = SCountriesFilters(country=country)
    data = await ArticlesServices(db).get_designers(filters)

    return {**status_ok, "data": data}


@articles_router.get("/manufacturers", summary="Список производителей")
async def get_manufacturers(
        db: DDB,
        country: str | None = Query(None, description="Фильтр по стране"),
):
    """
    Получить список производителей
    """

    filters = SCountriesFilters(country=country)
    data = await ArticlesServices(db).get_manufacturers(filters)

    return {**status_ok, "data": data}
