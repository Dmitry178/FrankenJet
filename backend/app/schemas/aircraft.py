from datetime import date
from pydantic import BaseModel, Field
from uuid import UUID

from app.db.models.aircraft import EngineTypes, AircraftStatus


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

    slug: str = Field(..., max_length=64, description="Строковый идентификатор")
    name: str = Field(..., max_length=32, description="Название")
    manufacturer_id: UUID = Field(None, description="ID производителя")
    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    aircraft_type: str = Field(None, max_length=32, description="Тип воздушного судна")  # TODO: уточнить длину (enum)
    first_flight: date = Field(None, description="Первый полёт")
    wingspan: float = Field(None, description="Размах крыльев в метрах")
    length: float = Field(None, description="Длина воздушного судна в метрах")
    height: float = Field(None, description="Высота воздушного судна в метрах")
    max_takeoff_weight: float = Field(None, description="Максимальный взлетный вес в килограммах")
    engine_type: str = Field(None, max_length=32, description="Тип двигателя")  # TODO: уточнить длину (enum)
    number_of_engines: int = Field(None, description="Количество двигателей")
    max_speed: int = Field(None, description="Максимальная скорость в км/ч")
    cruise_speed: int = Field(None, description="Крейсерская скорость в км/ч")
    range: int = Field(None, description="Дальность полета в км")
    service_ceiling: int = Field(None, description="Практический потолок в метрах")
    crew: int = Field(None, description="Экипаж (количество человек)")
    # capacity: int = Field(None, description="Вместимость (количество пассажиров или полезной нагрузки)")
    icao_designator: str = Field(None, max_length=4, description="Четырёхбуквенный код ИКАО")
    iata_designator: str = Field(None, max_length=3, description="Двух-трёхбуквенный код ИАТА")
    status: str = Field(None, max_length=32, description="Статус самолета")  # TODO: уточнить длину (enum)
    # variants: str = Field(None, description="Описание модификаций и вариантов самолета")
    year_of_manufacture: int = Field(None, description="Дата начала производства")
    first_used: date = Field(None, description="Дата начала эксплуатации")
    last_used: date = Field(None, description="Дата окончания эксплуатации")


class SCountriesFilters(BaseModel):
    """
    Схема фильтра по странам
    """

    country: str | None = Field(None, description="Страна"),


class SCountries(BaseModel):
    """
    Схема стран
    """

    id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    name: str = Field(None, max_length=32, description="Название страны")
    iso_code: str | None = Field(None, max_length=3, description="Трёхбуквенный ISO-код страны")
    flag_image_url: str = Field(None, max_length=128, description="URL изображения флага страны")


class SDesigners(BaseModel):
    """
    Схема конструкторов
    """

    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    slug: str = Field(..., max_length=64, description="Строковый идентификатор")
    name: str = Field(..., max_length=32, description="Имя конструктора")
    birth_date: date = Field(None)
    death_date: date = Field(None)
    known_for: str = Field(None, description="Чем знаменит конструктор")
    biography: str = Field(..., description="Биография")
    image_url: str = Field(None, description="URL основного изображения")


class SDesignBureaus(BaseModel):
    """
    Схема конструкторских бюро
    """

    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    slug: str = Field(..., max_length=64, description="Строковый идентификатор")
    name: str = Field(..., max_length=32, description="Название конструкторского бюро")
    description: str = Field(..., description="Описание конструкторского бюро")


class SManufacturers(BaseModel):
    """
    Схема производителей
    """

    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    slug: str = Field(..., max_length=64, description="Строковый идентификатор")
    name: str = Field(..., max_length=32, description="Название производителя")
    description: str = Field(..., description="Описание производителя")
