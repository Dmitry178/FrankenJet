from uuid import UUID

from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.countries import SCountriesFilters
from app.schemas.manufacturers import SManufacturers


class ManufacturersServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @handle_basic_db_errors
    async def get_manufacturers(self, filters: SCountriesFilters | None = None):
        """
        Получение списка производителей
        """

        filter_by = filters.model_dump(exclude_none=True) if filters else {}
        return await self.db.aircraft.manufacturers.select_all(filter_by)

    @handle_basic_db_errors
    async def add_manufacturer(self, data: SManufacturers):
        """
        Добавление карточки производителя
        """

        return await self.db.aircraft.manufacturers.insert_one(data)

    @handle_basic_db_errors
    async def edit_manufacturer(self, manufacturer_id: UUID, data: SManufacturers, exclude_unset=False):
        """
        Редактирование карточки производителя
        """

        return await self.db.aircraft.manufacturers.update(
            data,
            id=manufacturer_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    @handle_basic_db_errors
    async def delete_manufacturer(self, manufacturer_id: UUID):
        """
        Удаление карточки производителя
        """

        return await self.db.aircraft.manufacturers.delete(id=manufacturer_id)
