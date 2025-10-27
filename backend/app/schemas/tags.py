from pydantic import BaseModel, Field


class STags(BaseModel):
    """
    Схема модели тегов
    """

    tag_id: str = Field(..., max_length=32, description="Название тега")


class STagsPut(BaseModel):
    """
    Схема редактирование тегов (PUT)
    """

    old_value: str = Field(..., max_length=32, description="Старое название тега")
    new_value: str = Field(..., max_length=32, description="Новое название тега")
