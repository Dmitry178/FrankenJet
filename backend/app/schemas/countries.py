from pydantic import BaseModel, Field


class SCountriesFilters(BaseModel):
    """
    Схема фильтра по странам
    """

    country: str | None = Field(None, description="Страна")


class SCountries(BaseModel):
    """
    Схема модели стран
    """

    id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    name: str = Field(..., max_length=32, description="Название страны")
    iso_code: str | None = Field(None, max_length=3, description="Трёхбуквенный ISO-код страны")
    flag_image_url: str | None = Field(None, max_length=128, description="URL изображения флага страны")
