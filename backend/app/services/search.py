from app.config.env import settings
from app.core import ESManager
from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.search import SSearch


class SearchService:

    db: DBManager | None
    es: ESManager | None

    def __init__(self, db: DBManager | None = None, es: ESManager | None = None) -> None:
        self.db = db
        self.es = es

    @handle_basic_db_errors
    async def search(self, data: SSearch):
        """
        Обработка поискового запроса
        """

        # если Elasticsearch доступен, ищем через него
        if self.es:
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": data.query,
                                    "fields": ["title^2", "content", "tags^1.5", "summary^1.2"]
                                }
                            }
                        ]
                    }
                },
                "from": (data.page - 1) * data.per_page,
                "size": data.per_page,
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {},
                        "summary": {}
                    }
                }
            }

            # фильтрация по категориям
            if data.categories:
                search_body["query"]["bool"]["filter"] = [
                    {"terms": {"category": ", ".join(data.categories)}}
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
                    "page": data.page,
                    "per_page": data.per_page
                }

        # если Elasticsearch не настроен, либо выдал ошибку, то запускаем простой поиск по базе
        fallback_result = await self.db.articles.search(data)
        for item in fallback_result["results"]:
            if item.get("image_url"):
                item["image_url"] = settings.S3_DIRECT_URL + item["image_url"]

        return fallback_result
