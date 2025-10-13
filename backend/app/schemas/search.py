from pydantic import BaseModel, Field


class SSearch(BaseModel):
    """
    Схема поискового запроса
    """

    query: str | None = Field(None, max_length=256, description="Поисковый запрос")
    categories: list | None = Field(None, max_length=128, description="Список категорий статей")
    page: int = Field(1, ge=1, description="Номер страницы")
    per_page: int = Field(20, ge=1, le=100, description="Количество статей на странице")
