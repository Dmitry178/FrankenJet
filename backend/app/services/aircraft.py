from typing import List

from app.db.db_manager import DBManager
from app.db.models import Aircraft
from app.db.models.articles import AircraftTypes, EngineTypes, AircraftStatus
from app.schemas.aircraft import SAircraftFilters


class AircraftServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    async def get_aircraft(
            self,
            name: str | None = None,
            page: int | None = None,
            page_size: int | None = None,
            filters: SAircraftFilters | None = None):
        """
        Список воздушных судов по фильтру
        """

        filter_conditions = [Aircraft.name.ilike(f"%{name}%")] if name else []
        filter_by_conditions = filters.model_dump(exclude_none=True) if filters else {}

        offset = (page-1)*page_size
        limit = page_size

        return await self.db.articles.aircraft.select_all_paginated(
            offset, limit, *filter_conditions, **filter_by_conditions
        )

    @staticmethod
    async def get_aircraft_types() -> List[str]:
        """
        Список типов воздушных судов
        """

        return [AircraftTypes(item).value for item in AircraftTypes]

    @staticmethod
    async def get_engine_types() -> List[str]:
        """
        Список типов двигателей
        """

        return [EngineTypes(item).value for item in EngineTypes]

    @staticmethod
    async def get_aircraft_statuses() -> List[str]:
        """
        Список статусов воздушных судов
        """

        return [AircraftStatus(item).value for item in AircraftStatus]
