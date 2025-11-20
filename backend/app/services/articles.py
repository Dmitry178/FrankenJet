from typing import List
from uuid import UUID

from app.config.env import settings
from app.core.db_manager import DBManager
from app.db.models.aircraft import AircraftTypes, EngineTypes, AircraftStatus, AircraftPurpose
from app.db.models.articles import ArticleCategories, Articles
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.aircraft import SAircraft
from app.schemas.articles import SArticles


class ArticlesServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @staticmethod
    async def get_article_categories() -> List[str]:
        """
        Получение списка категорий статей
        """

        return [ArticleCategories(item).value for item in ArticleCategories]

    @handle_basic_db_errors
    async def get_article(self, slug: str) -> dict:
        """
        Загрузка статьи по slug
        """

        data = await self.db.articles.get_article_by_slug(slug)
        if not data:
            return {}

        if data.get("Aircraft"):
            aircraft = SAircraft.model_validate(data.get("Aircraft"), from_attributes=True)
            if aircraft.image_url:
                aircraft.image_url = f"{settings.S3_DIRECT_URL}{aircraft.image_url}"
        else:
            aircraft = None

        result = {
            "article": data.get("Articles"),
            "aircraft": aircraft,
        }

        return result

    @handle_basic_db_errors
    async def get_articles_list_filtered(
            self,
            filters: str | None = None,
            page: int | None = None,
            page_size: int | None = None,
    ) -> List[Articles]:
        """
        Получение списка статей с фильтром
        """

        filter_conditions = [Articles.title.ilike(f"%{filters}%")] if filters else []

        if page is None or page_size is None:
            return await self.db.articles.select_all_paginated(*filter_conditions)

        offset = (page-1)*page_size
        limit = page_size

        return await self.db.articles.select_all_paginated(
            offset, limit, *filter_conditions
        )

    @staticmethod
    def distribute_tags_by_category(tags: list[str]) -> dict[str, list[str]]:
        """
        Распределение тегов по категориям
        """

        groups = {
            "countries": [],
            "aircraft_types": [],
            "engine_types": [],
            "aircraft_status": [],
            "aircraft_purpose": [],
        }

        for tag in tags:
            if tag in AircraftTypes:
                groups["aircraft_types"].append(tag)
            elif tag in EngineTypes:
                groups["engine_types"].append(tag)
            elif tag in AircraftStatus:
                groups["aircraft_status"].append(tag)
            elif tag in AircraftPurpose:
                groups["aircraft_purpose"].append(tag)
            else:
                groups["countries"].append(tag)

        return groups

    @handle_basic_db_errors
    async def get_articles_list_tags(
            self,
            tags: str | None = None,
            page: int | None = None,
            page_size: int | None = None
    ) -> list[Articles]:
        """
        Получение списка статей с заданными тегами с пагинацией
        """

        tags_list = []

        # формирование списка тегов из строки
        if tags:
            tags_raw_list = tags.split(",")
            tags_list = [tag.strip() for tag in tags_raw_list if tag.strip()]

        # распределение тегов по группам
        groups = self.distribute_tags_by_category(tags_list)

        if page is None or page_size is None:
            # вызов с использованием значений по умолчанию для offset и limit
            return await self.db.articles.select_articles_groups_paginated(groups)

        offset = (page - 1) * page_size
        limit = page_size

        return await self.db.articles.select_articles_groups_paginated(groups, offset, limit)

    @handle_basic_db_errors
    async def add_article(self, data: SArticles):
        """
        Добавление статьи
        """

        return await self.db.articles.insert_one(data, commit=True)

    @handle_basic_db_errors
    async def edit_article(self, article_id: UUID, data: SArticles, exclude_unset=False):
        """
        Редактирование статьи
        """

        return await self.db.articles.update(
            data,
            id=article_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    @handle_basic_db_errors
    async def delete_article(self, article_id: UUID):
        """
        Удаление статьи
        """

        return await self.db.articles.delete(id=article_id)
