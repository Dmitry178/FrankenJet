import asyncio
import secrets
import signal
import uvicorn

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.api import router
from app.config.env import settings, AppMode
from app.consumers.startup import run_consumers
from app.core import rmq_manager, cache_manager, es_manager
from app.core.logs import logger
from app.core.shutdown import shutdown_event
from app.exceptions.api import csrf_token_error


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


if settings.APP_MODE == AppMode.production and settings.SWAGGER_AVAILABLE_IN_PROD:
    prefix = settings.SWAGGER_URL_PREFIX if settings.SWAGGER_URL_PREFIX else ""
    app_params = {"docs_url": f"/{prefix}docs", "redoc_url": f"/{prefix}redoc", "openapi_url": f"/{prefix}openapi"}
elif settings.APP_MODE == AppMode.production:
    app_params = {"docs_url": None, "redoc_url": None, "openapi_url": None}
else:
    app_params = {}

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan, **app_params)

# установка CORS
if settings.get_cors:
    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=settings.get_cors,
        allow_credentials=True,
        allow_methods=["OPTIONS", "GET", "POST", "PUT", "PATCH", "DELETE"],  # отключаем TRACE и CONNECT
        allow_headers=["*"],  # "Content-Type", "Authorization", "Accept", "X-Requested-With", # "User-Agent"  # TODO
        # expose_headers=[],
        # max_age=600,
    )


@app.middleware("http")
async def csrf_protect_middleware(request: Request, call_next):
    """
    Проверка CSRF-токена в production
    """

    if settings.APP_MODE != AppMode.production:
        return await call_next(request)

    # исключение эндпоинтов Swagger UI и ReDoc из CSRF-проверки (если задано в настройках)
    if settings.SWAGGER_CSRF_EXCLUDE_IN_PROD and request.url.path.startswith(("/docs", "/redoc")):
        return await call_next(request)

    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        # извлечение токена из заголовка
        csrf_token_header = request.headers.get("X-CSRF-Token")
        # извлечение токена из куки
        csrf_token_cookie = request.cookies.get("csrf-token")

        if not csrf_token_header or not csrf_token_cookie or csrf_token_header != csrf_token_cookie:
            return csrf_token_error

    response = await call_next(request)

    # установка куки с CSRF-токеном
    if "csrf-token" not in request.cookies:
        token = secrets.token_urlsafe(32)
        # httponly=False для доступа frontend к cookie с токеном
        response.set_cookie("csrf-token", token, httponly=False, samesite="lax")

    return response


# подключение роутеров
app.include_router(router)


def signal_handler():
    """
    Обработчик сигналов, установка события завершения
    """

    logger.info("Signal received")
    shutdown_event.set()


async def run_api():
    """
    Запуск API
    """

    # создание конфигурации uvicorn
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, reload=True)
    server = uvicorn.Server(config)

    # запуск сервера в фоновой задаче
    server_task = asyncio.create_task(server.serve())

    try:
        await shutdown_event.wait()

    finally:
        server.should_exit = True  # команда остановки
        try:
            # ожидание завершения задачи сервера
            await server_task
        except asyncio.CancelledError:
            logger.info("Shutting down...")


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
