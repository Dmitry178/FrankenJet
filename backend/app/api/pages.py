from fastapi import APIRouter

from app.core.logs import logger
from app.dependencies.db import DDB
from app.services.pages import PagesService
from app.types import status_ok, status_error

pages_router = APIRouter(prefix="/pages", tags=["Pages"])


@pages_router.get("/home", summary="Информация для главной страницы")
async def home(db: DDB):
    """
    Получение информации для главной страницы
    """

    try:
        data = await PagesService(db).home()
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)
        return status_error
