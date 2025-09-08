from pydantic import BaseModel, Field

from app.db.models.articles import EngineTypes, AircraftStatus


class SAircraftFilters(BaseModel):
    """
    Схема фильтров воздушных судов
    """

    country: str | None = Field(None, description="Страна"),
    engine_type: EngineTypes | None = Field(None, description="Тип двигателя"),
    status: AircraftStatus | None = Field(None, description="Статусу воздушного судна"),


class SCountriesFilters(BaseModel):
    """
    Схема фильтра по странам
    """

    country: str | None = Field(None, description="Страна"),
