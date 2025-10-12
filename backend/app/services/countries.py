from uuid import UUID

from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.aircraft import SCountries


class CountriesServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @handle_basic_db_errors
    async def get_countries(self):
        """
        Получение списка стран
        """

        return await self.db.aircraft.countries.select_all()

    @handle_basic_db_errors
    async def add_country(self, data: SCountries):
        """
        Добавление карточки страны
        """

        return await self.db.aircraft.countries.insert_one(data)

    @handle_basic_db_errors
    async def edit_country(self, aircraft_id: UUID, data: SCountries, exclude_unset=False):
        """
        Редактирование карточки страны
        """

        return await self.db.aircraft.countries.update(
            data,
            id=aircraft_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    @handle_basic_db_errors
    async def delete_country(self, aircraft_id: UUID):
        """
        Удаление карточки страны
        """

        return await self.db.aircraft.countries.delete(id=aircraft_id)
