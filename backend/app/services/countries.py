from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.countries import SCountries


class CountriesServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @handle_basic_db_errors
    async def get_countries(self):
        """
        Получение списка стран
        """

        return await self.db.directory.countries.select_all()

    @handle_basic_db_errors
    async def add_country(self, data: SCountries):
        """
        Добавление карточки страны
        """

        return await self.db.directory.countries.insert_one(data)

    @handle_basic_db_errors
    async def edit_country(self, country_id: str, data: SCountries, exclude_unset=False):
        """
        Редактирование карточки страны
        """

        return await self.db.directory.countries.update(
            data,
            id=country_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    @handle_basic_db_errors
    async def delete_country(self, country_id: str):
        """
        Удаление карточки страны
        """

        return await self.db.directory.countries.delete(id=country_id)
