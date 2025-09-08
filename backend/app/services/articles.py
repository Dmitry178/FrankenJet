from app.db.db_manager import DBManager
from app.schemas.aircraft import SCountriesFilters


class ArticlesServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def get_countries(self):
        """
        Получить список стран
        """

        return await self.db.articles.countries.select_all()

    async def get_design_bureaus(self, filters: SCountriesFilters | None = None):
        """
        Получить список конструкторских бюро
        """

        filter_by = filters.model_dump(exclude_none=True) if filters else {}
        return await self.db.articles.design_bureaus.select_all(filter_by)

    async def get_designers(self, filters: SCountriesFilters | None = None):
        """
        Получить список конструкторов
        """

        filter_by = filters.model_dump(exclude_none=True) if filters else {}
        return await self.db.articles.designers.select_all(filter_by)

    async def get_manufacturers(self, filters: SCountriesFilters | None = None):
        """
        Получить список производителей
        """

        filter_by = filters.model_dump(exclude_none=True) if filters else {}
        return await self.db.articles.manufacturers.select_all(filter_by)
