from datetime import date
from pydantic import BaseModel, Field


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
    name: str = Field(..., max_length=32, description="Название конструкторского бюро")
    description: str = Field(..., description="Описание конструкторского бюро")


class SManufacturers(BaseModel):
    """
    Схема производителей
    """

    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    name: str = Field(..., max_length=32, description="Название производителя")
    description: str = Field(..., description="Описание производителя")
