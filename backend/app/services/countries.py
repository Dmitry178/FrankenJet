from uuid import UUID

from app.db.db_manager import DBManager
from app.schemas.aircraft import SCountries


class CountriesServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def get_countries(self):
        """
        Получение списка стран
        """

        return await self.db.aircraft.countries.select_all()

    async def add_country(self, data: SCountries):
        """
        Добавление карточки страны
        """

        return await self.db.aircraft.countries.insert_one(data)

    async def edit_country(self, aircraft_id: UUID, data: SCountries, exclude_unset=False):
        """
        Редактирование карточки страны
        """

        return await self.db.aircraft.countries.update_one(
            data,
            id=aircraft_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    async def delete_country(self, aircraft_id: UUID):
        """
        Удаление карточки страны
        """

        return await self.db.aircraft.countries.delete_one(id=aircraft_id)
