from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, call

from app.exceptions.base import BaseCustomException
from app.types import status_ok


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


async def test_api_tags_return(ac: AsyncClient, admin_user_token):
    """
    Тестирование return API тегов
    """

    with patch("app.api.tags.TagsServices.auto_create", new_callable=AsyncMock) as mock_auto_create:
        service_return_value = None
        api_expected_value = {**status_ok}
        mock_auto_create.return_value = service_return_value

        response = await ac.post("/tags/generate")
        assert response.status_code == 201
        response_json = response.json()
        assert response_json == api_expected_value

        mock_auto_create.assert_called_once_with()

    with patch("app.api.tags.TagsServices.get_tags", new_callable=AsyncMock) as mock_get_tags:
        service_return_value = "data"
        api_expected_value = {**status_ok, "data": service_return_value}
        mock_get_tags.return_value = service_return_value

        response = await ac.get("/tags")
        assert response.status_code == 200
        response_json = response.json()
        assert response_json == api_expected_value

        mock_get_tags.assert_called_once_with()

    with patch("app.api.tags.TagsServices.add_tag", new_callable=AsyncMock) as mock_add_tag:
        service_return_value = "data"
        api_expected_value = {**status_ok, "data": service_return_value}
        mock_add_tag.return_value = service_return_value

        response = await ac.post("/tags", json={"tag": "some tag"})
        assert response.status_code == 201
        response_json = response.json()
        assert response_json == api_expected_value

        mock_add_tag.assert_called_once_with("some tag")

    with patch("app.api.tags.TagsServices.edit_tag", new_callable=AsyncMock) as mock_edit_tag:
        params = {"old_value": "some tag", "new_value": "some tag 2"}

        mock_edit_tag.return_value = None
        response = await ac.put("/tags", json=params)
        assert response.status_code == 404
        mock_edit_tag.assert_called_once_with("some tag", "some tag 2")

        service_return_value = "data"
        api_expected_value = {**status_ok, "data": service_return_value}
        mock_edit_tag.return_value = service_return_value
        response = await ac.put("/tags", json=params)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json == api_expected_value
        assert mock_edit_tag.call_count == 2
        mock_edit_tag.assert_has_calls([
            call('some tag', 'some tag 2'),
            call('some tag', 'some tag 2')
        ])

    with patch("app.api.tags.TagsServices.delete_tag", new_callable=AsyncMock) as mock_delete_tag:
        service_return_value = 1
        api_expected_value = {**status_ok, "data": {"rows": service_return_value}}
        mock_delete_tag.return_value = service_return_value

        response = await ac.delete("/tags/some%20tag")
        assert response.status_code == 200
        response_json = response.json()
        assert response_json == api_expected_value

        mock_delete_tag.assert_called_once_with("some tag")


async def test_api_tags_db_error(ac: AsyncClient, admin_user_token):
    """
    Тестирование обработки ошибок БД
    """

    expected_detail = "Bad Request"
    expected_status_code = 400

    with patch("app.api.tags.TagsServices.auto_create", new_callable=AsyncMock) as mock_auto_create:
        mock_auto_create.side_effect = BaseCustomException(detail=expected_detail, status_code=expected_status_code)
        response = await ac.post("/tags/generate")
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")

    with patch("app.api.tags.TagsServices.get_tags", new_callable=AsyncMock) as mock_get_tags:
        mock_get_tags.side_effect = BaseCustomException(detail=expected_detail, status_code=expected_status_code)
        response = await ac.get("/tags")
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")

    with patch("app.api.tags.TagsServices.delete_tag", new_callable=AsyncMock) as mock_delete_tag:
        mock_delete_tag.side_effect = BaseCustomException(detail=expected_detail, status_code=expected_status_code)
        response = await ac.delete("/tags/some%20tag")
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")
