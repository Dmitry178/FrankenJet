"""
Схема приведена для примера, в текущей итерации проекта не используется.
"""

from datetime import date
from pydantic import BaseModel, Field


class SDesigners(BaseModel):
    """
    Схема конструкторов
    """

    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    name: str = Field(..., max_length=32, description="Имя конструктора")
    birth_date: date | None = Field(None)
    death_date: date | None = Field(None)
    known_for: str | None = Field(None, description="Чем знаменит конструктор")
    biography: str = Field(..., description="Биография")
    image_url: str | None = Field(None, description="URL основного изображения")
