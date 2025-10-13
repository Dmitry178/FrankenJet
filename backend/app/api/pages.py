from fastapi import APIRouter

from app.core import cache_manager
from app.core.logs import logger
from app.dependencies.db import DDB
from app.exceptions.base import BaseCustomException
from app.services.pages import PagesService
from app.types import status_ok

pages_router = APIRouter(prefix="/pages", tags=["Pages"])


@pages_router.get("/home", summary="Информация для главной страницы")
@cache_manager.cached(ttl=720)
async def home(db: DDB):
    """
    Получение информации для главной страницы
    """

    try:
        data = await PagesService(db).home()
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response
