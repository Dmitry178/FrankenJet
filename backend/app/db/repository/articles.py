from sqlalchemy import select, func, true, case, literal, union_all, cast, String
from sqlalchemy.orm import selectinload

from app.db.models import Articles, Aircraft, Facts, ArticlesTagsAssociation, Countries
from app.db.repository.base import BaseRepository
from app.schemas.search import SSearch


class ArticlesRepository(BaseRepository):
    """
    Репозиторий модели статей
    """

    model = Articles

    async def get_random_articles(self, limit: int = None):
        """
        Загрузка случайных статей
        """

        query = (
            select(Articles.slug, Articles.title, Articles.summary, Aircraft.image_url)
            .select_from(Articles)
            .join(Aircraft, Aircraft.article_id == Articles.id)
            .where(Articles.is_published == true())
            .order_by(func.random())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.mappings().all()

    async def get_article_by_slug(self, slug: str):
        """
        Загрузка статьи по slug
        """

        query = (
            select(Articles)
            .options(selectinload(Articles.aircraft))
            .options(selectinload(Articles.tags))
            .filter(Articles.slug == slug)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def search(self, data: SSearch):
        """
        Поиск по всем категориям
        """

        query = data.query
        page = data.page
        page_size = data.page_size
        search_term = f"%{query}%"

        # подзапросы для каждой сущности
        aircraft_query = (
            select(
                cast(Articles.id, String).label("id"),
                Articles.article_category.label("category"),
                Articles.slug,
                Articles.title,
                Articles.summary,
                Articles.published_at,
                Aircraft.image_url,
            )
            .select_from(Articles)
            .outerjoin(Aircraft, Aircraft.article_id == Articles.id)
            .where(
                Articles.is_published.is_(True),
                Articles.is_archived.is_(False),
                Articles.title.ilike(search_term) |
                Articles.summary.ilike(search_term) |
                Articles.content.ilike(search_term) |
                Aircraft.name.ilike(search_term) |
                Aircraft.original_name.ilike(search_term) |
                Aircraft.icao_designator.ilike(search_term) |
                Aircraft.iata_designator.ilike(search_term)
            )
        )

        facts_query = (
            select(
                cast(Facts.id, String).label("id"),
                literal("facts").label("category"),
                literal(None).label("slug"),
                literal(None).label("title"),
                Facts.fact.label("summary"),
                literal(None).label("published_at"),
                literal(None).label("image_url"),
            )
            .where(Facts.fact.ilike(search_term))
        )

        # объединение всех подзапросов
        combined_query = union_all(
            aircraft_query,
            facts_query
        ).alias("combined")

        # подсчёт общего количества статей
        total_count_query = select(func.count()).select_from(combined_query)
        total_count_result = await self.session.execute(total_count_query)
        total_count = total_count_result.scalar()

        # подсчёт количества категорий
        all_categories_query = select(combined_query.c.category).distinct()
        all_categories_result = await self.session.execute(all_categories_query)
        all_categories = [row.category for row in all_categories_result.fetchall()]

        # подсчёт количества по категориям
        category_counts_query = select(
            func.sum(
                case(
                    (combined_query.c.category == "aircraft", 1),  # noqa
                    else_=0
                )
            ).label("aircraft_count"),
            func.sum(
                case(
                    (combined_query.c.category == "facts", 1),  # noqa
                    else_=0
                )
            ).label("facts_count")
        ).select_from(combined_query)

        category_counts_result = await self.session.execute(category_counts_query)
        counts = category_counts_result.fetchone()

        total_categories = (
            (1 if counts.aircraft_count else 0) +
            (1 if counts.facts_count else 0)
        )

        # выбираем результаты с пагинацией
        offset_value = (page - 1) * page_size
        paginated_query = (
            select(combined_query)
            .order_by(combined_query.c.published_at.desc().nullslast())
            .offset(offset_value)
            .limit(page_size)
        )

        result = await self.session.execute(paginated_query)
        rows = result.fetchall()

        # возвращаем результат
        return {
            "results": [
                {
                    "id": row.id,
                    "category": row.category,
                    "slug": row.slug,
                    "title": row.title,
                    "summary": row.summary,
                    "published_at": row.published_at,
                    "image_url": row.image_url,
                }
                for row in rows
            ],
            "metadata": {
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size,
                "total_categories": total_categories,
            },
            "categories": all_categories,
        }

    async def select_articles_list_paginated(self, tags: list[str] | None = None, offset: int = 0, limit: int = None):
        """
        Получение списка статей по списку тегов с пагинацией
        """

        query = (
            select(
                Articles.id.label("id"),
                Articles.slug,
                Articles.title,
                Articles.summary,
                Aircraft.image_url,
            )
            .select_from(Articles)
            .join(Aircraft, Aircraft.article_id == Articles.id)
            .join(ArticlesTagsAssociation, ArticlesTagsAssociation.article_id == Articles.id)
            .where(
                Articles.is_published.is_(True),
                Articles.is_archived.is_(False),
            )
            .distinct()
            .offset(offset)
        )

        if tags:
            query = query.where(ArticlesTagsAssociation.tag_id.in_(tags))

        if limit is not None:
            query = query.limit(limit)

        return (await self.session.execute(query)).mappings().all()

    async def select_articles_groups_paginated(
            self,
            groups: dict[str, list[str]] | None = None,
            offset: int = 0,
            limit: int = None
    ):
        """
        Получение списка статей по группам тегов с пагинацией
        """

        query = (
            select(
                Articles.id.label("id"),
                Articles.slug,
                Articles.title,
                Articles.summary,
                Aircraft.image_url,
            )
            .select_from(Articles)
            .join(Aircraft, Aircraft.article_id == Articles.id)
            .join(Countries, Countries.id == Aircraft.country_id)
            .join(ArticlesTagsAssociation, ArticlesTagsAssociation.article_id == Articles.id)
            .where(
                Articles.is_published.is_(True),
                Articles.is_archived.is_(False),
            )
            .distinct()
            .offset(offset)
        )

        if groups:
            if countries := groups.get("countries"):
                query = query.where(Countries.name.in_(countries))
            if aircraft_types := groups.get("aircraft_types"):
                query = query.where(Aircraft.aircraft_type.in_(aircraft_types))
            if engine_types := groups.get("engine_types"):
                query = query.where(Aircraft.engine_type.in_(engine_types))
            if aircraft_status := groups.get("aircraft_status"):
                query = query.where(Aircraft.status.in_(aircraft_status))
            if aircraft_purpose := groups.get("aircraft_purpose"):
                query = query.where(Aircraft.aircraft_purpose.in_(aircraft_purpose))

        if limit is not None:
            query = query.limit(limit)

        return (await self.session.execute(query)).mappings().all()

    async def get_articles_slugs(self):
        """
        Получение списка slug статей
        """

        query = (
            select(Articles.slug, Articles.published_at)
            .filter(Articles.is_published.is_(True), Articles.is_archived.is_(False))
        )
        return (await self.session.execute(query)).mappings().all()
