from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID

from app.db.models.articles import EngineTypes, AircraftStatus


class SAircraftFilters(BaseModel):
    """
    Схема фильтров воздушных судов
    """

    country: str | None = Field(None, description="Страна"),
    engine_type: EngineTypes | None = Field(None, description="Тип двигателя"),
    status: AircraftStatus | None = Field(None, description="Статусу воздушного судна"),


class SPostAircraft(BaseModel):
    """
    Схема воздушного судна
    """

    name: str  # название
    manufacturer_id: UUID | None  # id производителя
    country_id: str | None  # код страны
    aircraft_type: str | None  # тип воздушного судна
    first_flight: date | None  # первый полёт
    wingspan: float | None  # размах крыльев в метрах
    length: float | None  # длина воздушного судна в метрах
    height: float | None  # высота воздушного судна в метрах
    max_takeoff_weight: float | None  # максимальный взлетный вес в килограммах
    engine_type: str | None  # тип двигателя
    number_of_engines: int | None  # количество двигателей
    max_speed: int | None  # максимальная скорость в км/ч
    cruise_speed: int | None  # крейсерская скорость в км/ч
    range: int | None  # дальность полета в км
    service_ceiling: int | None  # практический потолок в метрах
    crew: int | None  # экипаж (количество человек)
    # capacity: int | None  # вместимость (количество пассажиров или полезной нагрузки)
    icao_designator: str | None  # четырёхбуквенный код ИКАО
    iata_designator: str | None  # двух-трёхбуквенный код ИАТА
    status: str | None  # статус самолета
    # variants: str_256 | None  # описание модификаций и вариантов самолета
    year_of_manufacture: int | None  # дата начала производства
    first_used: date | None  # дата начала эксплуатации
    last_used: date | None  # дата окончания эксплуатации
