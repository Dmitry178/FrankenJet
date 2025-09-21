import enum

from datetime import datetime

from sqlalchemy import Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from app.db import Base
from app.db.models.base import TimestampMixin
from app.db.types import uid_pk, int_0, str_64, str_128, str_256, str_512, str_1024, bool_false

if TYPE_CHECKING:
    from app.db.models import Aircraft


class ArticleCategories(str, enum.Enum):
    """
    Категории статей
    """

    aircraft = "aircraft"
    designer = "designer"
    manufacturer = "manufacturer"
    design_bureau = "design_bureau"


class Articles(Base, TimestampMixin):
    """
    Статьи
    """

    __tablename__ = "articles"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    article_category: Mapped[str | None] = mapped_column(Enum(ArticleCategories, native_enum=False))  # категория

    slug: Mapped[str_64] = mapped_column(unique=True)  # строковый идентификатор
    title: Mapped[str_64] = mapped_column(unique=True)  # заголовок статьи
    summary: Mapped[str_1024 | None]  # краткое описание статьи  # TODO: исправить размер строки
    content: Mapped[str] = mapped_column(Text)  # текст статьи
    image_url: Mapped[str_128 | None]  # главное изображение
    thumbnail_url: Mapped[str_128 | None]  # миниатюра
    meta_title: Mapped[str_512 | None]  # мета-информация для SEO (название)  # TODO: исправить размер строки
    meta_description: Mapped[str_1024 | None]  # мета-информация для SEO (описание)  # TODO: исправить размер строки
    view_count: Mapped[int_0]  # количество просмотров страницы
    seo_keywords: Mapped[str_256 | None]  # ключевые слова SEO  # TODO: исправить размер строки

    is_published: Mapped[bool_false]  # статья опубликована
    is_archived: Mapped[bool_false]  # статья в архиве
    published_at: Mapped[datetime | None]  # дата публикации
    archived_at: Mapped[datetime | None]  # дата архива

    aircraft: Mapped["Aircraft"] = relationship(back_populates="article")
