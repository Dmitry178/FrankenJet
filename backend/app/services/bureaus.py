from uuid import UUID

from app.core.db_manager import DBManager
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.countries import SCountriesFilters
from app.schemas.design_bureaus import SDesignBureaus


class BureausServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @handle_basic_db_errors
    async def get_design_bureaus(self, filters: SCountriesFilters | None = None):
        """
        Получение списка конструкторских бюро
        """

        filter_by = filters.model_dump(exclude_none=True) if filters else {}
        return await self.db.aircraft.design_bureaus.select_all(filter_by)

    @handle_basic_db_errors
    async def add_design_bureau(self, data: SDesignBureaus):
        """
        Добавление карточки конструкторского бюро
        """

        return await self.db.aircraft.design_bureaus.insert_one(data)

    @handle_basic_db_errors
    async def edit_design_bureau(self, design_bureaus_id: UUID, data: SDesignBureaus, exclude_unset=False):
        """
        Редактирование карточки конструкторского бюро
        """

        return await self.db.aircraft.design_bureaus.update(
            data,
            id=design_bureaus_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    @handle_basic_db_errors
    async def delete_design_bureau(self, design_bureaus_id: UUID):
        """
        Удаление карточки конструкторского бюро
        """

        return await self.db.aircraft.design_bureaus.delete(id=design_bureaus_id)
