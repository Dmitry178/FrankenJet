import asyncio
import signal
import sys
import uvicorn

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import router
from app.api.local import index_local_router
from app.config.env import settings, AppMode
from app.consumers.startup import run_consumers
from app.core import rmq_manager, cache_manager, es_manager
from app.core.logs import logger


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):  # noqa
    """
    Точка входа при запуске и завершении FastAPI
    """

    if rmq_manager.url:
        await rmq_manager.start()
        logger.info("RabbitMQ connected")

    if cache_manager.url:
        await cache_manager.start()
        logger.info("Redis connected")

    if es_manager.url:
        await es_manager.start()
        logger.info("ElasticSearch connected")

    message = f"App started at: {datetime.now()} [{settings.BUILD}]"
    logger.info(message)

    yield

    if es_manager.url:
        await es_manager.stop()
        logger.info("ElasticSearch stopped")

    if cache_manager.url:
        await cache_manager.close()
        logger.info("Redis disconnected")

    if rmq_manager.url:
        await rmq_manager.close()
        logger.info("RabbitMQ disconnected")

    message = f"App stopped at: {datetime.now()} [{settings.BUILD}]"
    logger.info(message)

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


# Установка CORS
if settings.get_cors:
    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=settings.get_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Подключение роутеров
if settings.APP_MODE == AppMode.local:
    app.include_router(index_local_router)

app.include_router(router)


def signal_handler():
    logger.info("Shutting down...")
    sys.exit(0)


async def run_api():
    """
    Запуск API
    """

    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, reload=True)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    """
    Запуск API совместно с RabbitMQ consumers для локальной разработки.
    В production запускать по отдельности: uvicorn (main.py) и cкрипт запуска консьюмера
    /backend/app/consumers/startup.py
    """

    # обработка сигналов
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)  # noqa

    if settings.APP_MODE == AppMode.local:
        # запуск API и консьюмера в режиме локальной разработки
        await asyncio.gather(run_api(), run_consumers())
    else:
        # в режиме production - запуск только API (консьюмер должен запускаться в endpoint.sh)
        await run_api()


if __name__ == "__main__":
    asyncio.run(main())
