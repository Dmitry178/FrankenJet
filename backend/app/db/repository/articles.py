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

    async def search(self, query: str, page: int, per_page: int):
        """
        Поиск по всем категориям
        """

        search_term = f"%{query}%"

        # подзапросы для каждой сущности
        article_query = (
            select(
                cast(Articles.id, String).label("id"),
                Articles.slug,
                Articles.title,
                Articles.summary,
                Articles.content,
                Articles.article_category,
                literal("article").label("entity_type"),
                Articles.published_at,
            )
            .where(
                Articles.is_published.is_(True),
                Articles.is_archived.is_(False),
                Articles.title.ilike(search_term) |
                Articles.summary.ilike(search_term) |
                Articles.content.ilike(search_term)
            )
        )

        aircraft_query = (
            select(
                cast(Aircraft.id, String).label("id"),
                Articles.slug,
                Aircraft.name.label("title"),
                Aircraft.original_name.label("summary"),
                literal(None).label("content"),
                literal(None).label("article_category"),
                literal("aircraft").label("entity_type"),
                Articles.published_at,
            )
            .join(Articles, Aircraft.article_id == Articles.id)
            .where(
                Articles.is_published.is_(True),
                Articles.is_archived.is_(False),
                Aircraft.name.ilike(search_term) |
                Aircraft.original_name.ilike(search_term) |
                Aircraft.icao_designator.ilike(search_term) |
                Aircraft.iata_designator.ilike(search_term)
            )
        )

        fact_query = (
            select(
                cast(Facts.id, String).label("id"),
                literal(None).label("slug"),
                Facts.fact.label("title"),
                literal(None).label("summary"),
                literal(None).label("content"),
                literal(None).label("article_category"),
                literal("fact").label("entity_type"),
                literal(None).label("published_at"),
            )
            .where(Facts.fact.ilike(search_term))
        )

        # Объединяем все подзапросы
        combined_query = union_all(
            article_query,
            aircraft_query,
            fact_query
        ).alias("combined")

        # Подсчитываем общее количество
        total_count_query = select(func.count()).select_from(combined_query)
        total_count_result = await self.session.execute(total_count_query)
        total_count = total_count_result.scalar()

        # Подсчитываем количество по категориям
        category_counts_query = select(
            func.sum(
                case(
                    (combined_query.c.entity_type == "aircraft", 1),  # noqa
                    else_=0
                )
            ).label('aircraft_count'),
            func.sum(
                case(
                    (combined_query.c.entity_type == "fact", 1),  # noqa
                    else_=0
                )
            ).label('fact_count')
        ).select_from(combined_query)

        category_counts_result = await self.session.execute(category_counts_query)
        counts = category_counts_result.fetchone()

        total_categories = (
                (1 if counts.aircraft_count else 0) +
                (1 if counts.fact_count else 0)
        )

        # Выбираем результаты с пагинацией
        offset_value = (page - 1) * per_page
        paginated_query = (
            select(combined_query)
            .order_by(combined_query.c.published_at.desc().nullslast())
            .offset(offset_value)
            .limit(per_page)
        )

        result = await self.session.execute(paginated_query)
        rows = result.fetchall()

        # Возвращаем результат
        return {
            "results": [
                {
                    "id": row.id,
                    "slug": row.slug,
                    "title": row.title,
                    "summary": row.summary,
                    "entity_type": row.entity_type,
                    "published_at": row.published_at,
                }
                for row in rows
            ],
            "total_count": total_count,
            "total_pages": (total_count + per_page - 1) // per_page,
            "total_categories": total_categories
        }
