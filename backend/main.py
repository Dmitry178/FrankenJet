from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routes.auth import auth_router
from app.api.routes.local import index_local_router
from app.core.config import settings, AppMode
from app.core.logs import logger


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """
    Точка входа при запуске и завершении FastAPI
    """

    message = f'App started at: {datetime.now()} [{settings.VERSION}]'
    logger.info(message)

    yield

    message = f'App stopped at: {datetime.now()} [{settings.VERSION}]'
    logger.info(message)

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


# Установка CORS
if settings.get_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Подключение роутеров
if settings.APP_MODE == AppMode.local:
    app.include_router(index_local_router)

app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8111, reload=True)
