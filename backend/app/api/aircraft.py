from fastapi import APIRouter, Query, Path, Depends
from uuid import UUID

from app.core.logs import logger
from app.db.models.aircraft import EngineTypes, AircraftStatus
from app.dependencies.auth import get_auth_editor_id
from app.dependencies.db import DDB
from app.schemas.aircraft import SAircraftFilters, SAircraft
from app.services.aircraft import AircraftServices
from app.types import status_ok, status_error

aircraft_router = APIRouter(prefix="/aircraft", tags=["Aircraft"])


@aircraft_router.get("/{slug}", summary="Карточка воздушного судна")
async def get_aircraft(
        db: DDB,
        slug: str = Path(..., description="Название воздушного судна"),
):
    """
    Карточка воздушного судна
    """

    try:
        data = await AircraftServices(db).get_aircraft(slug)
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@aircraft_router.get("/list", summary="Список воздушных судов")
async def get_aircraft_list(
        db: DDB,
        name: str | None = Query(None, description="Название воздушного судна"),
        country: str | None = Query(None, description="Фильтр по стране"),
        engine_type: EngineTypes | None = Query(None, description="Фильтр по типу двигателя"),
        status: AircraftStatus | None = Query(None, description="Фильтр по статусу воздушного судна"),
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
):
    """
    Получение списка воздушных судов
    """

    try:
        filters = SAircraftFilters(
            country=country,
            engine_type=engine_type,
            status=status,
        )

        data = await AircraftServices(db).get_aircraft_list(name, page, page_size, filters)
        return {**status_ok, "data": data}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@aircraft_router.post(
    "",
    summary="Добавление воздушного судна",
    dependencies=[Depends(get_auth_editor_id)],
)
async def add_aircraft(data: SAircraft, db: DDB):
    """
    Добавление карточки воздушного судна
    """

    try:
        result = AircraftServices(db).add_aircraft(data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@aircraft_router.put(
    "/{aircraft_id}",
    summary="Изменение воздушного судна",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_aircraft_put(aircraft_id: UUID, data: SAircraft, db: DDB):
    """
    Редактирование карточки воздушного судна (put)
    """

    try:
        result = AircraftServices(db).edit_aircraft(aircraft_id, data)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@aircraft_router.patch(
    "/{aircraft_id}",
    summary="Изменение воздушного судна",
    dependencies=[Depends(get_auth_editor_id)],
)
async def edit_aircraft_post(aircraft_id: UUID, data: SAircraft, db: DDB):
    """
    Редактирование карточки воздушного судна (patch)
    """

    try:
        result = AircraftServices(db).edit_aircraft(aircraft_id, data, exclude_unset=True)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@aircraft_router.delete(
    "/{aircraft_id}",
    summary="Удаление воздушного судна",
    dependencies=[Depends(get_auth_editor_id)],
)
async def delete_aircraft(aircraft_id: UUID, db: DDB):
    """
    Удаление карточки воздушного судна
    """

    try:
        result = AircraftServices(db).delete_aircraft(aircraft_id)
        return {**status_ok, "data": result}

    except Exception as ex:
        logger.exception(ex)
        return status_error


@aircraft_router.get("/types", summary="Список типов воздушных судов")
async def get_aircraft_types():
    """
    Получение списка типов воздушных судов
    """

    # try/except не нужно, данные берутся из enum
    data = await AircraftServices().get_aircraft_types()
    return {**status_ok, "data": data}


@aircraft_router.get("/engines", summary="Список типов двигателей воздушных судов")
async def get_engine_types():
    """
    Получение списка типов двигателей воздушных судов
    """

    # try/except не нужно, данные берутся из enum
    data = await AircraftServices().get_engine_types()
    return {**status_ok, "data": data}


@aircraft_router.get("/statuses", summary="Список статусов воздушных судов")
async def get_aircraft_statuses():
    """
    Получение списка статусов воздушных судов
    """

    # try/except не нужно, данные берутся из enum
    data = await AircraftServices().get_aircraft_statuses()
    return {**status_ok, "data": data}
