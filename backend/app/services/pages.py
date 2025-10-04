from app.core.db_manager import DBManager


class PagesService:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def home(self) -> dict:
        """
        Информация для главной страницы
        """

        context = {}

        # случайные статьи
        columns = ["slug", "title", "summary"]
        random_articles = await self.db.articles.select_random(columns=columns, limit=3, is_published=True) or []
        context["articles"] = random_articles

        # случайные факты
        random_facts = await self.db.facts.select_random(limit=5) or []
        context["facts"] = [item["fact"] for item in random_facts]

        return context
