from pydantic import BaseModel, Field


class STags(BaseModel):
    """
    Схема модели тегов
    """

    tag_id: str = Field(..., max_length=16, description="Название тега")
