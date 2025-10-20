from app.config.env import settings
from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors


class PagesService:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @handle_basic_db_errors
    async def home(self) -> dict:
        """
        Информация для главной страницы
        """

        context = {}

        # случайные статьи
        random_articles = await self.db.articles.get_random_articles(limit=3) or []

        # обработка изображений
        processed_articles = [
            {
                **article,
                "image_url": f"{settings.S3_DIRECT_URL}{article['image_url']}" if article["image_url"] else None
            }
            for article in random_articles
        ]

        # случайные факты
        random_facts = await self.db.facts.select_random(limit=5) or []

        # сборка контекста
        context["articles"] = processed_articles
        context["facts"] = [item["fact"] for item in random_facts]

        return context
