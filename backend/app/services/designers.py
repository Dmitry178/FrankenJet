from uuid import UUID

from app.core.db_manager import DBManager
from app.schemas.aircraft import SCountriesFilters, SDesigners


class DesignersServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def get_designers(self, filters: SCountriesFilters | None = None):
        """
        Получение списка конструкторов
        """

        filter_by = filters.model_dump(exclude_none=True) if filters else {}
        return await self.db.aircraft.designers.select_all(filter_by)

    async def add_designer(self, data: SDesigners):
        """
        Добавление карточки конструктора
        """

        return await self.db.aircraft.designers.insert_one(data)

    async def edit_designer(self, designer_id: UUID, data: SDesigners, exclude_unset=False):
        """
        Редактирование карточки конструктора
        """

        return await self.db.aircraft.designers.update_one(
            data,
            id=designer_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    async def delete_designer(self, designer_id: UUID):
        """
        Удаление карточки конструктора
        """

        return await self.db.aircraft.designers.delete_one(id=designer_id)
