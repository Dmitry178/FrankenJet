async def test_api_pages(ac):
    """
    Тестирование данных для веб-страниц
    """

    response = await ac.get("/pages/home")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["status"] == "ok", "Ошибка получения данных страницы home"

    # проверка данных пользователя
    assert response_json.get("data"), "Ответ не содержит данных"
    assert response_json["data"].get("articles"), "Ответ не содержит списка статей"
    assert len(response_json["data"].get("articles")) > 0, "Ответ не содержит статей"
    assert response_json["data"].get("facts"), "Ответ не содержит списка фактов"
    assert len(response_json["data"].get("facts")) > 0, "Ответ не содержит фактов"
