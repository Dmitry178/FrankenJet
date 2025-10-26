import pytest

from httpx import AsyncClient

from app.schemas.auth import SLoginUser

email = "email@example.com"
password = "password"


async def test_api_create_user(ac: AsyncClient):
    """
    Тестирование регистрации пользователя
    """

    # регистрация пользователя
    data = SLoginUser(
        email=email,
        password=password
    )

    response = await ac.post(
        "/auth/register",
        json=data.model_dump()
    )
    assert response.status_code == 201, "Ошибка статуса первичного создания пользователя"
    assert response.json().get("status") == "ok", "Ошибка операции создания пользователя"

    # повторная регистрация пользователя
    response = await ac.post(
        "/auth/register",
        json=data.model_dump()
    )
    assert response.json()["status"] == "error", "Ошибка статуса повторного пользователя"


@pytest.mark.parametrize("email_, password_, status_code_, status_", [
    (f"0{email}", password, 404, "error"),
    (email, f"0{password}", 401, "error"),
    (email, password, 200, "ok"),
    (1234, "password", 422, ""),
])
async def test_api_login_user(ac: AsyncClient, email_: str, password_: str, status_code_: str, status_: str):
    """
    Тестирование аутентификации пользователя
    """

    # попытка логина
    response = await ac.post(
        "/auth/login",
        json={"email": email_, "password": password_}
    )
    assert response.status_code == status_code_, "Ошибка кода статуса"
    if response.status_code != 200:
        return

    assert response.json().get("status") == status_
    if response.json()["status"] != "ok":
        return

    # получение токена пользователя
    access_token = response.json().get("data", {}).get("tokens", {}).get("access_token", "")
    assert access_token, "Токен отсутствует"
    ac.headers.update({"Authorization": f"Bearer {access_token}"})

    # проверка аутентификации
    response = await ac.get("/auth/info")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("status", "") == "ok"
    assert response_json.get("data")
    assert response_json["data"].get("user")
    assert response_json["data"].get("roles") == []
    assert response_json["data"].get("user", {}).get("email") == email_
