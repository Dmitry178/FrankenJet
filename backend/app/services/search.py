from app.config.env import settings
from app.core import ESManager
from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.search import SSearch

# название индекса
ARTICLES_INDEX = "articles"


class SearchService:

    db: DBManager | None
    es: ESManager | None

    def __init__(self, db: DBManager | None = None, es: ESManager | None = None) -> None:
        self.db = db
        self.es = es
        self.index = [ARTICLES_INDEX]

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

            result = await self.es.search(search_body, index=self.index)

            if result:
                hits = result.get("hits", {}).get("hits", [])
                total = result.get("hits", {}).get("total", {}).get("value", 0)

                if hits:
                    results = []
                    categories_set = set()

                    for hit in hits:
                        src = hit["_source"]
                        category = src.get("category")
                        categories_set.add(category)

                        # обработка подсвеченных фрагментов
                        highlight = hit.get("highlight", {})
                        summary_fragments = []

                        # добавление результатов в заголовках
                        if "title" in highlight and "content" not in highlight:
                            summary_fragments.extend(highlight["title"])

                        # добавление результатов в кратком содержании статьи
                        if "summary" in highlight and "content" not in highlight:
                            summary_fragments.extend(highlight["summary"])

                        # добавление результатов в содержимом статьи
                        if "content" in highlight:
                            summary_fragments.extend(highlight["content"])

                        if summary_fragments:
                            summary_text = " ... ".join(summary_fragments[:5])
                        else:
                            summary_text = src.get("summary") or (
                                src.get("content")[:420] + "..." if src.get("content") else "")

                        # формирование ответа
                        item = {
                            "id": str(src.get("id")),
                            "category": category,
                            "slug": src.get("slug"),
                            "title": src.get("title"),
                            "summary": summary_text,
                            "published_at": src.get("published_at"),
                            "image_url": (
                                settings.S3_DIRECT_URL + src["image_url"]
                                if src.get("image_url")
                                else None
                            ),
                        }

                        # Добавляем подсветку (опционально, если нужна фронту)
                        if "highlight" in hit:
                            item["highlight"] = hit["highlight"]

                        results.append(item)

                    all_categories = list(categories_set)
                    total_categories = len(all_categories)

                    return {
                        "results": results,
                        "metadata": {
                            "total_count": total,
                            "total_pages": (total + data.per_page - 1) // data.per_page,
                            "total_categories": total_categories,
                        },
                        "categories": all_categories,
                    }

        # если Elasticsearch не настроен, либо выдал ошибку, то запускаем простой поиск по базе
        fallback_result = await self.db.articles.search(data)
        for item in fallback_result["results"]:
            if item.get("image_url"):
                item["image_url"] = settings.S3_DIRECT_URL + item["image_url"]

        return fallback_result
