from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI

from app.config.env import settings, AppMode
from app.core import rmq_manager, cache_manager, es_manager, chatbot_settings
from app.core.db_manager import DBManager
from app.core.logs import logger
from app.core.logs_handlers import add_logging_handler
from app.db import async_session_maker
from app.services.bot import bot_services


def get_api_params():
    """
    Параметры FastAPI
    """

    if settings.APP_MODE == AppMode.production and settings.SWAGGER_AVAILABLE_IN_PROD:
        prefix = settings.SWAGGER_URL_PREFIX if settings.SWAGGER_URL_PREFIX else ""
        app_params = {"docs_url": f"/{prefix}docs", "redoc_url": f"/{prefix}redoc", "openapi_url": f"/{prefix}openapi"}
    elif settings.APP_MODE == AppMode.production:
        app_params = {"docs_url": None, "redoc_url": None, "openapi_url": None}
    else:
        app_params = {}

    return app_params


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):  # noqa
    """
    Точка входа при запуске и завершении FastAPI
    """

    if rmq_manager.url:
        await rmq_manager.start()
        logger.info("RabbitMQ connected")
        bot_services.rmq = rmq_manager
        await add_logging_handler(logger, bot_services)

    if cache_manager.url:
        await cache_manager.start()
        logger.info("Redis connected")

    if es_manager.url:
        await es_manager.start()
        logger.info("Elasticsearch connected")

    db_manager = DBManager(session_factory=async_session_maker)
    async with db_manager as db:
        try:
            await chatbot_settings.initialize(db=db)
            logger.info("Chatbot settings initialized")
        except Exception as ex:
            logger.exception(ex)

    message = f"App started at: {datetime.now()}"
    logger.info(message)
    await bot_services.send_info("Сервис запущен 🟢")

    yield

    if es_manager.url:
        await es_manager.close()
        logger.info("Elasticsearch stopped")

    if cache_manager.url:
        await cache_manager.close()
        logger.info("Redis disconnected")

    if rmq_manager.url:
        await bot_services.send_info("Сервис остановлен 🔴")
        await rmq_manager.close()
        logger.info("RabbitMQ disconnected")

    message = f"App stopped at: {datetime.now()}"
    logger.info(message)
