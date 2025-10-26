import json

from httpx import AsyncClient


async def test_api_search(ac: AsyncClient):
    """
    Тестирование поиска
    """

    response = await ac.post(
        url="/search",
        json={
            "query": "flyer",
        }
    )
    assert response.status_code == 200, "Ошибка в GET /search"

    response_json = response.json()
    response_json["data"]["results"][0].pop("published_at")
    response_json["data"]["results"][0].pop("image_url")

    with open("tests/mocks/articles.json", "r") as file:
        mock_articles = json.load(file)

    expected_data = [data for data in mock_articles if data["slug"] == "wright-flyer"][0]
    expected_data["category"] = expected_data["article_category"]
    expected_data.pop("article_category")
    expected_data.pop("content")
    expected_data.pop("meta_title")
    expected_data.pop("meta_description")
    expected_data.pop("seo_keywords")
    expected_data.pop("is_published")

    expected_json = {
        "status": "ok",
        "data": {
            "results": [expected_data],
            "metadata": {
                "total_count": 1,
                "total_pages": 1,
                "total_categories": 1
            },
            "categories": [
                "aircraft"
            ]
        }
    }

    assert response_json == expected_json
