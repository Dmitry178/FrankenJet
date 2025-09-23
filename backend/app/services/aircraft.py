from typing import List
from uuid import UUID

from app.db.db_manager import DBManager
from app.db.models import Aircraft
from app.db.models.aircraft import AircraftTypes, EngineTypes, AircraftStatus
from app.schemas.aircraft import SAircraftFilters, SAircraft


class AircraftServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @staticmethod
    async def get_aircraft_types() -> List[str]:
        """
        Получение списка типов воздушных судов
        """

        return [AircraftTypes(item).value for item in AircraftTypes]

    @staticmethod
    async def get_engine_types() -> List[str]:
        """
        Получение списка типов двигателей
        """

        return [EngineTypes(item).value for item in EngineTypes]

    @staticmethod
    async def get_aircraft_statuses() -> List[str]:
        """
        Получение списка статусов воздушных судов
        """

        return [AircraftStatus(item).value for item in AircraftStatus]

    async def get_aircraft(self, slug: str) -> Aircraft:
        """
        Получение карточки воздушного судна
        """

        return await self.db.aircraft.select_one_or_none(slug=slug)

    async def get_aircraft_list(
            self,
            name: str | None = None,
            page: int | None = None,
            page_size: int | None = None,
            filters: SAircraftFilters | None = None
    ) -> List[Aircraft]:
        """
        Получение списка воздушных судов по фильтру
        """

        filter_conditions = [Aircraft.name.ilike(f"%{name}%")] if name else []
        filter_by_conditions = filters.model_dump(exclude_none=True) if filters else {}

        if page is None or page_size is None:
            return await self.db.aircraft.aircraft.select_all(
                *filter_conditions, **filter_by_conditions
            )

        offset = (page-1)*page_size
        limit = page_size

        return await self.db.aircraft.aircraft.select_all_paginated(
            offset, limit, *filter_conditions, **filter_by_conditions
        )

    async def add_aircraft(self, data: SAircraft):
        """
        Добавление карточки воздушного судна
        """

        return await self.db.aircraft.aircraft.insert_one(data)

    async def edit_aircraft(self, aircraft_id: UUID, data: SAircraft, exclude_unset=False):
        """
        Редактирование карточки воздушного судна
        """

        return await self.db.aircraft.aircraft.update_one(
            data,
            id=aircraft_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    async def delete_aircraft(self, aircraft_id: UUID):
        """
        Удаление карточки воздушного судна
        """

        return await self.db.aircraft.aircraft.delete_one(id=aircraft_id)
