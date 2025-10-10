from sqlalchemy import select, func, true, case, literal, union_all, cast, String

from app.db.models import Articles, Aircraft, Designers, Manufacturers, DesignBureaus, Facts
from app.db.repository.base import BaseRepository


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
            select(Articles, Aircraft)
            .outerjoin(Aircraft, Articles.id == Aircraft.article_id)
            .outerjoin(Designers, Designers.id == Aircraft.article_id)
            .outerjoin(Manufacturers, Manufacturers.id == Aircraft.article_id)
            .outerjoin(DesignBureaus, DesignBureaus.id == Aircraft.article_id)
            .filter(Articles.slug == slug)
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.mappings().one_or_none()

    async def search(self, query: str, categories: list, page: int, per_page: int):
        """
        Поиск по всем категориям
        """

        # TODO: добавить категории в поиск

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

        # TODO: добавить остальные сущности

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
        offset_value = (page - 1) * per_page
        paginated_query = (
            select(combined_query)
            .order_by(combined_query.c.published_at.desc().nullslast())
            .offset(offset_value)
            .limit(per_page)
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
                "total_pages": (total_count + per_page - 1) // per_page,
                "total_categories": total_categories,
            },
            "categories": all_categories,
        }
