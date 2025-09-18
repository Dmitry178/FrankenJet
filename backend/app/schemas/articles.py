from datetime import datetime
from pydantic import BaseModel, Field


class SArticles(BaseModel):
    """
    Схема статей
    """

    article_category: str = Field(None, max_length=32, description="Категория статьи")  # TODO: уточнить длину (enum)
    slug: str = Field(..., max_length=64, description="Строковый идентификатор")
    title: str = Field(..., max_length=32, description="Заголовок статьи")
    summary: str = Field(None, description="Краткое описание статьи")
    content: str = Field(..., description="Текст статьи")
    image_url: str = Field(None, max_length=128, description="Главное изображение")
    thumbnail_url: str = Field(None, max_length=128, description="Миниатюра")
    meta_title: str = Field(None, max_length=64, description="Мета-информация для SEO (название)")
    meta_description: str = Field(None, max_length=128, description="Мета-информация для SEO (описание)")
    view_count: int = Field(..., ge=0, description="Количество просмотров страницы")
    seo_keywords: str = Field(None, max_length=128, description="Ключевые слова SEO")
    is_published: bool = Field(False, description="Статья опубликована")
    is_archived: bool = Field(False, description="Статья в архиве")
    published_at: datetime = Field(None, description="Дата публикации")
    archived_at: datetime = Field(None, description="Дата архива")
