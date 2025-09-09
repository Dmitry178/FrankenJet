from pydantic import BaseModel, Field


class SCountriesFilters(BaseModel):
    """
    Схема фильтра по странам
    """

    country: str | None = Field(None, description="Страна"),
