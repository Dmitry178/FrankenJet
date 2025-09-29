from fastapi import APIRouter
from starlette.responses import RedirectResponse

from app.config.env import settings, AppMode

index_local_router = APIRouter(tags=["Local"])


@index_local_router.get("/", include_in_schema=False, summary="Редирект на Swagger UI")
async def index():
    """
    Перенаправление на Swagger UI в локальном режиме работы приложения
    """

    if settings.APP_MODE != AppMode.local:
        return {"detail": "Not Found"}

    return RedirectResponse("/docs")
