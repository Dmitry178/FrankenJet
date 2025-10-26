import json
import os
import pytest

from httpx import AsyncClient
from unittest.mock import patch

from app.exceptions.api import settings_error


async def test_api_settings(ac: AsyncClient):
    """
    Тестирование получения настроек приложения через API
    """

    def str_to_bool(value: str) -> bool | None:
        value = value.lower()
        return True if value == "true" else False if value == "false" else None

    response = await ac.get("/settings")
    assert response.status_code == 200, "Ошибка в GET /settings"

    # проверка полученных данных
    response_json = response.json()
    expected_json = {
        "status": "ok",
        "data": {
            "auth_methods": {
                "authentication": str_to_bool(os.environ["ALLOW_AUTHENTICATION"]),
                "registration": str_to_bool(os.environ["ALLOW_REGISTRATION"]),
                "reset_password": str_to_bool(os.environ["ALLOW_RESET_PASSWORD"]),
                "oauth2_google": str_to_bool(os.environ["ALLOW_OAUTH2_GOOGLE"]),
                "oauth2_vk": str_to_bool(os.environ["ALLOW_OAUTH2_VK"]),
            }
        }
    }
    assert response_json == expected_json, "Ошибка ответа в GET /settings"


@pytest.mark.asyncio
async def test_api_settings_service_exception(ac: AsyncClient):
    """
    Тестирование случая, когда AppServices.get_settings() выбрасывает исключение
    """

    expected_content = json.loads(settings_error.body.decode(settings_error.charset))

    with patch("app.services.app.AppServices.get_settings", side_effect=AttributeError("Settings not loaded")):
        response = await ac.get("/settings")
        assert response.status_code == 503
        response_json = response.json()
        assert response_json == expected_content
