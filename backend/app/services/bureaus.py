from uuid import UUID

from app.core.db_manager import DBManager
from app.schemas.aircraft import SCountriesFilters, SDesignBureaus


class BureausServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def get_design_bureaus(self, filters: SCountriesFilters | None = None):
        """
        Получение списка конструкторских бюро
        """

        filter_by = filters.model_dump(exclude_none=True) if filters else {}
        return await self.db.aircraft.design_bureaus.select_all(filter_by)

    async def add_design_bureau(self, data: SDesignBureaus):
        """
        Добавление карточки конструкторского бюро
        """

        return await self.db.aircraft.design_bureaus.insert_one(data)

    async def edit_design_bureau(self, design_bureaus_id: UUID, data: SDesignBureaus, exclude_unset=False):
        """
        Редактирование карточки конструкторского бюро
        """

        return await self.db.aircraft.design_bureaus.update_one(
            data,
            id=design_bureaus_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    async def delete_design_bureau(self, design_bureaus_id: UUID):
        """
        Удаление карточки конструкторского бюро
        """

        return await self.db.aircraft.design_bureaus.delete_one(id=design_bureaus_id)
