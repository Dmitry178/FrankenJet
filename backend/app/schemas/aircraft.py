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


class SAircraft(BaseModel):
    """
    Схема воздушного судна
    """

    name: str = Field(..., max_length=32, description="Название")
    manufacturer_id: UUID = Field(None, description="Id производителя")
    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    aircraft_type: str = Field(None, max_length=32, description="тип воздушного судна")  # TODO: уточнить длину (enum)
    first_flight: date = Field(None, description="первый полёт")
    wingspan: float = Field(None, description="размах крыльев в метрах")
    length: float = Field(None, description="длина воздушного судна в метрах")
    height: float = Field(None, description="высота воздушного судна в метрах")
    max_takeoff_weight: float = Field(None, description="максимальный взлетный вес в килограммах")
    engine_type: str = Field(None, max_length=32, description="тип двигателя")  # TODO: уточнить длину (enum)
    number_of_engines: int = Field(None, description="количество двигателей")
    max_speed: int = Field(None, description="максимальная скорость в км/ч")
    cruise_speed: int = Field(None, description="крейсерская скорость в км/ч")
    range: int = Field(None, description="дальность полета в км")
    service_ceiling: int = Field(None, description="практический потолок в метрах")
    crew: int = Field(None, description="экипаж (количество человек)")
    # capacity: int = Field(None, description="вместимость (количество пассажиров или полезной нагрузки)")
    icao_designator: str = Field(None, max_length=4, description="четырёхбуквенный код ИКАО")
    iata_designator: str = Field(None, max_length=3, description="двух-трёхбуквенный код ИАТА")
    status: str = Field(None, max_length=32, description="статус самолета")  # TODO: уточнить длину (enum)
    # variants: str = Field(None, description="описание модификаций и вариантов самолета")
    year_of_manufacture: int = Field(None, description="дата начала производства")
    first_used: date = Field(None, description="дата начала эксплуатации")
    last_used: date = Field(None, description="дата окончания эксплуатации")
