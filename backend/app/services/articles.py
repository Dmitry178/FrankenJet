from typing import List
from uuid import UUID

from app.db.db_manager import DBManager
from app.db.models.articles import ArticleCategories, Articles
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

    async def get_article(self, slug: str) -> Articles:
        """
        Получение статьи
        """

        return await self.db.articles.select_one_or_none(slug=slug)

    async def get_articles_list(
            self,
            page: int | None = None,
            page_size: int | None = None,
            filters: str | None = None,
    ) -> List[Articles]:
        """
        Получение списка статей с фильтром
        """

        filter_conditions = [Articles.title.ilike(f"%{filters}%")] if filters else []

        offset = (page-1)*page_size
        limit = page_size

        return await self.db.articles.select_all_paginated(
            offset, limit, *filter_conditions
        )

    async def add_article(self, data: SArticles):
        """
        Добавление статьи
        """

        return await self.db.articles.insert_one(data)

    async def edit_article(self, article_id: UUID, data: SArticles, exclude_unset=False):
        """
        Редактирование статьи
        """

        return await self.db.articles.update_one(
            data,
            id=article_id,
            exclude_unset=exclude_unset,
            commit=True,
        )

    async def delete_article(self, article_id: UUID):
        """
        Удаление статьи
        """

        return await self.db.articles.delete_one(id=article_id)
