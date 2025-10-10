from app.config.env import settings
from app.core import ESManager
from app.core.db_manager import DBManager


class SearchService:

    db: DBManager | None
    es: ESManager | None

    def __init__(self, db: DBManager | None = None, es: ESManager | None = None) -> None:
        self.db = db
        self.es = es

    async def search(self, query: str, categories: str, page: int, per_page: int):
        """
        Обработка поискового запроса
        """

        # если ES доступен, ищем через него
        if self.es:
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^2", "content", "tags^1.5", "summary^1.2"]
                                }
                            }
                        ]
                    }
                },
                "from": (page - 1) * per_page,
                "size": per_page,
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {},
                        "summary": {}
                    }
                }
            }

            # фильтрация по категориям
            if categories:
                search_body["query"]["bool"]["filter"] = [
                    {"terms": {"category": categories}}
                ]

            result = await self.es.search(search_body)

            if result:
                hits = result["hits"]["hits"]
                formatted_results = []
                for hit in hits:
                    item = hit["_source"]
                    # добавляем подсветку, если есть
                    if "highlight" in hit:
                        item["highlight"] = hit["highlight"]
                    formatted_results.append(item)

                total = result["hits"]["total"]["value"]
                return {
                    "items": formatted_results,
                    "total": total,
                    "page": page,
                    "per_page": per_page
                }

        # если ElasticSearch не настроен, либо выдал ошибку, то запускаем простой поиск по базе
        fallback_result = await self.db.articles.search(query, categories, page, per_page)
        for item in fallback_result["results"]:
            if item.get("image_url"):
                item["image_url"] = settings.S3_ENDPOINT_URL + item["image_url"]

        return fallback_result
