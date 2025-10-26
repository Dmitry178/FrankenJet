"""
Схема приведена для примера, в текущей итерации проекта не используется.
"""

from pydantic import BaseModel, Field


class SDesignBureaus(BaseModel):
    """
    Схема конструкторских бюро
    """

    country_id: str = Field(..., min_length=2, max_length=2, description="Двухбуквенный ISO-код страны")
    name: str = Field(..., max_length=32, description="Название конструкторского бюро")
    description: str = Field(..., description="Описание конструкторского бюро")
