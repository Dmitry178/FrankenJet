from fastapi import APIRouter, Query

from app.db.models.articles import EngineTypes, AircraftStatus
from app.dependencies.db import DDB
from app.schemas.aircraft import SAircraftFilters
from app.services.aircraft import AircraftServices
from app.types import status_ok

aircraft_router = APIRouter(prefix="/articles", tags=["Articles"])


@aircraft_router.get("/aircraft", summary="Список воздушных судов")
async def get_aircraft(
        db: DDB,
        name: str | None = Query(None, description="Название самолета"),
        country: str | None = Query(None, description="Фильтр по стране"),
        engine_type: EngineTypes | None = Query(None, description="Фильтр по типу двигателя"),
        status: AircraftStatus | None = Query(None, description="Фильтр по статусу воздушного судна"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
):
    """
    Получить список воздушных судов
    """

    filters = SAircraftFilters(
        country=country,
        engine_type=engine_type,
        status=status,
    )

    data = await AircraftServices(db).get_aircraft(name, page, page_size, filters)
    return {**status_ok, "data": data}


@aircraft_router.get("/aircraft/types", summary="Список типов воздушных судов")
async def get_aircraft_types():
    """
    Получить список типов воздушных судов
    """

    data = await AircraftServices().get_aircraft_types()
    return {**status_ok, "data": data}


@aircraft_router.get("/aircraft/engines", summary="Список типов двигателей воздушных судов")
async def get_engine_types():
    """
    Получить список типов двигателей воздушных судов
    """

    data = await AircraftServices().get_engine_types()
    return {**status_ok, "data": data}


@aircraft_router.get("/aircraft/statuses", summary="Список статусов воздушных судов")
async def get_aircraft_statuses():
    """
    Получить список статусов воздушных судов
    """

    data = await AircraftServices().get_aircraft_statuses()
    return {**status_ok, "data": data}
