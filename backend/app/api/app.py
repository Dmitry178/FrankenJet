from fastapi import APIRouter

from app.core.logs import logger
from app.services.app import AppServices
from app.types import status_ok, status_error

app_router = APIRouter(tags=["App"])


@app_router.get("/settings", summary="Настройки приложения")
async def get_app_settings():
    """
    Вывод настроек приложения
    """

    try:
        data = await AppServices.get_settings()
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)
        return status_error
