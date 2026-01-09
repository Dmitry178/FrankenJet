from fastapi import APIRouter, Depends

from app.core import cache_manager, chatbot_settings
from app.core.logs import logger
from app.dependencies.auth import get_auth_admin_id
from app.dependencies.db import DDB
from app.exceptions.api import settings_error, http_error_500
from app.exceptions.base import BaseCustomException
from app.schemas.chatbot import SChatBotSettings
from app.services.app import AppServices
from app.types import status_ok

app_router = APIRouter(tags=["App"])


@app_router.get("/settings", summary="Настройки приложения")
@cache_manager.cached(ttl=3600)
async def get_app_settings():
    """
    Вывод настроек приложения
    """

    try:
        data = AppServices.get_settings()
        return {**status_ok, "data": data}

    except (AttributeError, TypeError, Exception) as ex:
        logger.exception(ex)
        return settings_error


@app_router.get("/bot-settings", summary="Настройки бота", dependencies=[Depends(get_auth_admin_id)])
async def get_bot_settings(db: DDB):
    """
    Получение настроек чат-бота
    """

    try:
        data = await chatbot_settings.get_bot_settings(db)
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response

    except (RuntimeError, Exception) as ex:
        logger.exception(ex)
        return http_error_500


@app_router.put("/bot-settings", summary="Сохранение настроек бота", dependencies=[Depends(get_auth_admin_id)])
async def save_bot_settings(data: SChatBotSettings):
    """
    Сохранение настроек чат-бота
    """

    try:
        data = await chatbot_settings.update_bot_settings(data)
        return {**status_ok, "data": data}

    except BaseCustomException as ex:
        logger.exception(ex)
        return ex.json_response

    except (RuntimeError, Exception) as ex:
        logger.exception(ex)
        return http_error_500
