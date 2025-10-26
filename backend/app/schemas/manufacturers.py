"""
Схема приведена для примера, в текущей итерации проекта не используется.
"""

from pydantic import BaseModel, Field


class SManufacturers(BaseModel):
    """
    Схема модели производителей
    """

    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    name: str = Field(..., max_length=32, description="Название производителя")
    description: str = Field(..., description="Описание производителя")
