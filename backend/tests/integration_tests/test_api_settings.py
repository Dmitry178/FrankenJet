import os


async def test_api_settings(ac):
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
