from httpx import AsyncClient


async def test_api_tags(ac: AsyncClient, admin_user_token):
    """
    Тестирование API тегов
    """

    # проверка пустого списка тегов
    response = await ac.get("/tags")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("status") == "ok", "Ошибка получения данных GET /tags"
    assert "data" in response_json, "Ответ не содержит данных"
    assert response_json.get("data") == []

    # проверка генерации тегов незарегистрированным пользователем
    response = await ac.post("/tags/generate")
    assert response.status_code == 403, "Ошибка доступа к POST /tags/generate"

    # проверка добавления тега незарегистрированным пользователем
    response = await ac.post("/tags", json={"tag": "some tag"})
    assert response.status_code == 403, "Ошибка доступа к POST /tags"

    # проверка генерации тегов зарегистрированным пользователем
    ac.headers.update({"Authorization": f"Bearer {admin_user_token}"})
    response = await ac.post("/tags/generate")
    assert response.status_code == 201
    response_json = response.json()
    assert response_json.get("status") == "ok", "Ошибка генерации данных POST /tags/generate"

    # проверка, что теги сгенерировались
    response = await ac.get("/tags")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("status") == "ok", "Ошибка получения данных GET /tags"
    assert "data" in response_json, "Ответ не содержит данных"
    assert len(response_json.get("data")) > 0, "Ошибка, данные не сгенерировались"

    # проверка добавления тега зарегистрированным пользователем
    response = await ac.post("/tags", json={"tag": "some tag"})
    assert response.status_code == 201

    response = await ac.post("/tags", json={"tag": "some tag 2"})
    assert response.status_code == 201

    response = await ac.post("/tags", json={"tag": "some tag"})
    assert response.status_code == 409

    # проверка валидации добавления тега
    response = await ac.post("/tags", json={"tag": "some tag" * 10})
    assert response.status_code == 422

    # проверка добавления тега
    response = await ac.get("/tags")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("status") == "ok", "Ошибка получения данных GET /tags"
    assert "data" in response_json, "Ответ не содержит данных"
    assert "some tag" in response_json.get("data"), "Ответ не содержит добавленного тега"

    # проверка редактирования тега (PUT)
    response = await ac.put("/tags", json={"old_value": "some tag", "new_value": "some tag 2"})
    assert response.status_code == 409

    response = await ac.put("/tags", json={"old_value": "some tag", "new_value": "some tag 3"})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("status") == "ok", "Ошибка получения данных PUT /tags"
    assert "data" in response_json, "Ответ не содержит данных"
    assert response_json.get("data") == "some tag 3", "Ошибка изменения данных"

    # проверка удаления тега
    response = await ac.delete("/tags/some%20tag%204")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("status") == "ok", "Ошибка получения данных DELETE /tags"
    assert response_json.get("data", {}).get("rows") == 0

    response = await ac.delete("/tags/some%20tag%203")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get("status") == "ok", "Ошибка получения данных DELETE /tags"
    assert response_json.get("data", {}).get("rows") == 1
