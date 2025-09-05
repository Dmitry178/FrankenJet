from fastapi import APIRouter

from app.services.app import AppServices

app_router = APIRouter(tags=["App"])


@app_router.get("/settings", summary="Настройки приложения")
async def get_app_settings():
    """
    Вывод настроек приложения
    """

    return await AppServices.get_settings()
