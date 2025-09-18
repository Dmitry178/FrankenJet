from uuid import UUID

from app.db.db_manager import DBManager
from app.schemas.aircraft import SCountriesFilters, SManufacturers


class ManufacturersServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def get_manufacturers(self, filters: SCountriesFilters | None = None):
        """
        Получение списка производителей
        """

        filter_by = filters.model_dump(exclude_none=True) if filters else {}
        return await self.db.aircraft.manufacturers.select_all(filter_by)

    async def add_manufacturer(self, data: SManufacturers):
        """
        Добавление карточки производителя
        """

        return await self.db.aircraft.manufacturers.insert_one(data)

    async def edit_manufacturer(self, manufacturer_id: UUID, data: SManufacturers, exclude_unset=False):
        """
        Редактирование карточки производителя
        """

        return await self.db.aircraft.manufacturers.update_one(
            data,
            id=manufacturer_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    async def delete_manufacturer(self, manufacturer_id: UUID):
        """
        Удаление карточки производителя
        """

        return await self.db.aircraft.manufacturers.delete_one(id=manufacturer_id)
