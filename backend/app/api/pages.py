from fastapi import APIRouter

from app.core import cache_manager
from app.core.logs import logger
from app.dependencies.db import DDB
from app.exceptions.base import BaseCustomException
from app.schemas.api import SuccessResponse
from app.services.pages import PagesService

pages_router = APIRouter(prefix="/pages", tags=["Pages"])


@pages_router.get("/home", summary="Информация для главной страницы")
@cache_manager.cached(ttl=3600)
async def home(db: DDB):
    """
    Получение информации для главной страницы
    """

    try:
        data = await PagesService(db).home()
        return SuccessResponse(data=data)

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response


@pages_router.get("/articles", summary="Информация для страницы статей")
async def home(db: DDB):
    """
    Получение информации для страницы статей
    """

    try:
        data = await PagesService(db).articles()
        return SuccessResponse(data=data)

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
