from app.core.db_manager import DBManager


class SearchService:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def search(self, query: str, page: int, per_page: int) -> dict:
        """
        Обработка поискового запроса
        """

        return await self.db.articles.search(query, page, per_page)
