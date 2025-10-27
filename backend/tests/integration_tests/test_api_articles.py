from unittest.mock import patch, AsyncMock

from httpx import AsyncClient
from uuid import UUID, uuid4

from app.exceptions.articles import ArticleNotFoundEx
from app.exceptions.base import BaseCustomException
from app.types import status_ok


async def test_api_articles_list(ac: AsyncClient):
    """
    Тестирование API получения списка статей
    """

    # проверка списка статей
    response = await ac.get("/articles/list")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json.get("status") == "ok", "Ошибка получения данных GET /articles/list"
    assert "data" in response_json, "Ответ не содержит данных"
    assert response_json.get("data")

    # проверка списка статей с фильтрами
    response = await ac.get("/articles/list?filters=string")
    assert response.status_code == 200
    response_json = response.json()
    data = response_json.get("data")
    assert isinstance(data, list)
    assert len(data) == 0

    # проверка списка статей с пагинацией за пределами списка
    response = await ac.get("/articles/list?page=100&page_size=20")
    assert response.status_code == 200
    response_json = response.json()
    data = response_json.get("data")
    assert isinstance(data, list)
    assert data == []

    # проверка списка статей с неправильным фильтром
    response = await ac.get("/articles/list?page=-1&page_size=10000000")
    assert response.status_code == 422


async def test_api_articles_create(ac: AsyncClient, moderator_user_token, editor_user_token, admin_user_token):
    """
    Тестирование API статьи (пользователями с разными ролями)
    """

    # данные статьи
    data = {
        "article_category": "aircraft",
        "slug": "string",
        "title": "string",
        "summary": "string",
        "content": "string",
        "meta_title": "string",
        "meta_description": "string",
        "seo_keywords": "string",
        "is_published": True,
        "is_archived": False,
    }

    # настройки проверяемых пользователей
    users = [
        {"role": "unregistered", "token": "", "status_codes":
            {"GET": 200, "POST": 403, "PUT": 403, "PATCH": 403, "DELETE": 403}},
        {"role": "moderator", "token": moderator_user_token, "status_codes":
            {"GET": 200, "POST": 403, "PUT": 403, "PATCH": 403, "DELETE": 403}},
        {"role": "editor", "token": editor_user_token, "status_codes":
            {"GET": 200, "POST": 201, "PUT": 200, "PATCH": 200, "DELETE": 403}},
        {"role": "admin", "token": admin_user_token, "status_codes":
            {"GET": 200, "POST": 201, "PUT": 200, "PATCH": 200, "DELETE": 200}},
    ]

    for user in users:

        # данные пользователя
        role_ = user["role"]
        status_codes_ = user["status_codes"]

        # авторизация
        if token_ := user["token"]:
            ac.headers.update({"Authorization": f"Bearer {token_}"})

        # -- проверка добавления статьи (метод POST)

        data_post = data.copy()
        data_post["slug"] = f'{data_post["slug"]}-{role_}'
        data_post["title"] = f'{data_post["title"]}-{role_}'

        response = await ac.post("/articles", json=data_post)
        status_code = response.status_code
        assert status_code == status_codes_["POST"], "Ошибка добавления статьи"

        if 200 <= status_code < 300:
            result = response.json()
            assert result.get("status") == "ok"
            added = result.get("data", {}).get("Articles")  # данные, добавленные в базу
            assert added, "Ошибка результатов добавления статьи"

            # ключи added, входящие в ключи словаря added_data
            added_subset = {key: added.get(key) for key in data_post.keys()}
            assert added_subset == data_post, "Результат добавления не совпадает с добавляемыми данными"

            article_id = added.get("id")
            slug = data_post["slug"]
            check_content = True
        else:
            # берём значения из mock-данных для попытки редактирования/удаления записи неавторизованными пользователями
            article_id = UUID("bfe94054-a0da-426a-862c-cdb90e1fa66e")
            slug = "wright-flyer"
            check_content = False

        # -- проверка получения статьи (метод GET)

        response = await ac.get(f"/articles/{slug}")
        status_code = response.status_code
        assert status_code == status_codes_["GET"], "Ошибка чтения статьи"

        result = response.json()
        assert result.get("status") == "ok"

        result_data = result.get("data", {}).get("article")
        assert result_data, "Ошибка результатов получения статьи"
        if check_content:
            subset = {key: result_data.get(key) for key in data_post.keys()}
            assert subset == data_post, "Результат полученных данных статьи не совпадает с добавляемыми ранее данными"

        # -- проверка редактирования статьи (метод PUT)

        data_put = data_post.copy()
        data_put["content"] = f'{data_put["content"]}-{role_}'
        response = await ac.put(f"/articles/{article_id}", json=data_put)
        status_code = response.status_code
        assert status_code == status_codes_["PUT"], "Ошибка изменения статьи (метод PUT)"

        if 200 <= status_code < 300:
            result = response.json()
            assert result.get("status") == "ok"

            result_data = result.get("data", {}).get("Articles")
            assert result_data, "Ошибка результатов получения статьи"
            subset = {key: result_data.get(key) for key in data_put.keys()}
            assert subset == data_put, "Результат изменённых данных статьи не совпадает с добавляемыми ранее данными"

        # -- проверка редактирования статьи (метод PATCH)
        data_patch = data_post.copy()
        data_patch["content"] = f'{data_patch["content"]}-{role_}'
        response = await ac.put(f"/articles/{article_id}", json=data_patch)
        status_code = response.status_code
        assert status_code == status_codes_["PATCH"], "Ошибка изменения статьи (метод PATCH)"

        if 200 <= status_code < 300:
            result = response.json()
            assert result.get("status") == "ok"

            result_data = result.get("data", {}).get("Articles")
            assert result_data, "Ошибка результатов получения статьи"
            subset = {key: result_data.get(key) for key in data_patch.keys()}
            assert subset == data_patch, "Результат изменённых данных статьи не совпадает с добавляемыми ранее данными"

        # -- проверка удаления статьи

        response = await ac.delete(f"/articles/{article_id}")
        status_code = response.status_code
        assert status_code == status_codes_["DELETE"], "Ошибка удаления статьи"

        if 200 <= status_code < 300:
            result = response.json()
            assert result.get("status") == "ok"
            assert result.get("data", {}).get("rows") == 1


async def test_api_articles(ac: AsyncClient, admin_user_token):
    """
    Тестирование неверных параметров API
    """

    data = {
        "article_category": "aircraft",
        "slug": "string",
        "title": "string",
        "summary": "string",
        "content": "string",
        "meta_title": "string",
        "meta_description": "string",
        "seo_keywords": "string",
        "is_published": True,
        "is_archived": False,
    }

    article_id = UUID("bfe94054-a0da-426a-862c-cdb90e1fa66e")  # значение взято из mock-данных

    wrong_article_id = uuid4()
    wrong_article_data = {"some_key": "some_value"}

    ac.headers.update({"Authorization": f"Bearer {admin_user_token}"})

    response = await ac.get("/articles/wrong-slug")
    assert response.status_code == 404

    response = await ac.post("/articles", json=wrong_article_data)
    assert response.status_code == 422

    response = await ac.put(f"/articles/{article_id}", json=wrong_article_data)
    assert response.status_code == 422

    response = await ac.put(f"/articles/{wrong_article_id}", json=data)
    assert response.status_code == 404

    response = await ac.patch(f"/articles/{article_id}", json=wrong_article_data)
    assert response.status_code == 422

    response = await ac.patch(f"/articles/{wrong_article_id}", json=data)
    assert response.status_code == 404

    response = await ac.delete(f"/articles/{wrong_article_id}")
    result = response.json()
    assert response.status_code == 200
    assert result.get("status") == "ok"
    assert result.get("data", {}).get("rows", None) == 0


async def test_api_articles_list_success_try_block(ac: AsyncClient):
    """
    Тестирование успешного сценария API получения списка статей (покрытие ветки try)
    """

    with patch(
            "app.services.articles.ArticlesServices.get_articles_list", new_callable=AsyncMock
    ) as mock_get_articles_list:
        expected_data = []
        mock_get_articles_list.return_value = expected_data

        response = await ac.get("/articles/list?filter=1234")

        assert response.status_code == 200
        response_json = response.json()
        assert response_json == {**status_ok, "data": expected_data}

        mock_get_articles_list.assert_called_once_with(1, 20, None)

    with patch("app.services.articles.ArticlesServices.get_article", new_callable=AsyncMock) as mock_get_articles:
        expected_data = None
        mock_get_articles.return_value = expected_data

        slug = "wright-flyer"
        response = await ac.get(f"/articles/{slug}")

        assert response.status_code == 404
        response_json = response.json()
        assert response_json == {"status": "error", "detail": "Статья не найдена"}

        mock_get_articles.assert_called_once_with("wright-flyer")

    with patch("app.services.articles.ArticlesServices.get_article", new_callable=AsyncMock) as mock_get_articles:
        expected_data = {"key": "value"}
        mock_get_articles.return_value = expected_data

        slug = "wright-flyer"
        response = await ac.get(f"/articles/{slug}")

        assert response.status_code == 200
        response_json = response.json()
        assert response_json == {**status_ok, "data": expected_data}

        mock_get_articles.assert_called_once_with("wright-flyer")


async def test_api_articles_db_error(ac: AsyncClient, admin_user_token):
    """
    Тестирование обработки ошибок БД
    """

    expected_detail = "Bad Request"
    expected_status_code = 400

    data = {
        "slug": "test-db",
        "title": "test-db",
        "content": "test-db",
    }

    article_id = UUID("bfe94054-a0da-426a-862c-cdb90e1fa66e")  # значение взято из mock-данных

    ac.headers.update({"Authorization": f"Bearer {admin_user_token}"})

    with patch("app.services.articles.ArticlesServices.get_article", new_callable=AsyncMock) as mock_get_article:
        mock_get_article.side_effect = BaseCustomException(
            detail=expected_detail, status_code=expected_status_code
        )

        response = await ac.get("/articles/wright-flyer")
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")

        mock_get_article.side_effect = ArticleNotFoundEx()
        response = await ac.get("/articles/wright-flyer")
        assert response.status_code == 404
        result = response.json()
        assert result.get("status") == "error"

    with patch(
            "app.services.articles.ArticlesServices.get_articles_list", new_callable=AsyncMock
    ) as mock_get_articles_list:
        mock_get_articles_list.side_effect = BaseCustomException(
            detail=expected_detail, status_code=expected_status_code
        )

        response = await ac.get("/articles/list?page=1&page_size=20")
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")

    with patch("app.services.articles.ArticlesServices.add_article", new_callable=AsyncMock) as mock_add_article:
        mock_add_article.side_effect = BaseCustomException(detail=expected_detail, status_code=expected_status_code)
        response = await ac.post("/articles", json=data)
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")

    with patch("app.services.articles.ArticlesServices.edit_article", new_callable=AsyncMock) as mock_edit_article:
        mock_edit_article.side_effect = BaseCustomException(detail=expected_detail, status_code=expected_status_code)

        response = await ac.put(f"/articles/{article_id}", json=data)
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")

        response = await ac.patch(f"/articles/{article_id}", json=data)
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")

    with patch("app.services.articles.ArticlesServices.delete_article", new_callable=AsyncMock) as mock_delete_article:
        mock_delete_article.side_effect = BaseCustomException(detail=expected_detail, status_code=expected_status_code)

        response = await ac.delete(f"/articles/{article_id}")
        assert response.status_code == expected_status_code
        result = response.json()
        assert result.get("status") == "error"
        assert expected_detail in result.get("detail", "")
