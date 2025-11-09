from sqlalchemy import update, select, literal_column, func, union_all

from app.db.models import Tags, Countries, Aircraft, Articles, ArticlesTagsAssociation, TagsCategories
from app.db.repository.base import BaseRepository


class TagsRepository(BaseRepository):
    """
    Репозиторий модели стран
    """

    model = Tags

    async def update_tag(self, old_value: str, new_value: str):
        """
        Редактирование тега
        """

        stmt = (
            update(self.model)
            .values(tag_id=new_value)
            .filter_by(tag_id=old_value)
            .returning(self.model.tag_id)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar()

    async def count_tags(self):
        """
        Подсчёт тегов во всех статьях
        """

        base_cte = (
            select(
                Countries.name.label("country"),
                Aircraft.aircraft_type,
                Aircraft.aircraft_purpose,
                Aircraft.engine_type,
                Aircraft.status,
            )
            .select_from(Articles)
            .join(Aircraft, Aircraft.article_id == Articles.id)
            .join(Countries, Countries.id == Aircraft.country_id)
            .where(
                Articles.is_published.is_(True),
                Articles.is_archived.is_(False),
            )
        ).cte("base_cte")

        country_counts = select(
            literal_column("'country'").label("type"),
            base_cte.c.country.label("value"),
            func.count().label("count")
        ).where(base_cte.c.country.isnot(None)).group_by(base_cte.c.country)

        aircraft_type_counts = select(
            literal_column("'aircraft_type'").label("type"),
            base_cte.c.aircraft_type.label("value"),
            func.count().label("count")
        ).where(base_cte.c.aircraft_type.isnot(None)).group_by(base_cte.c.aircraft_type)

        aircraft_purpose_counts = select(
            literal_column("'aircraft_purpose'").label("type"),
            base_cte.c.aircraft_purpose.label("value"),
            func.count().label("count")
        ).where(base_cte.c.aircraft_purpose.isnot(None)).group_by(base_cte.c.aircraft_purpose)

        engine_type_counts = select(
            literal_column("'engine_type'").label("type"),
            base_cte.c.engine_type.label("value"),
            func.count().label("count")
        ).where(base_cte.c.engine_type.isnot(None)).group_by(base_cte.c.engine_type)

        status_counts = select(
            literal_column("'status'").label("type"),
            base_cte.c.status.label("value"),
            func.count().label("count")
        ).where(base_cte.c.status.isnot(None)).group_by(base_cte.c.status)

        union_all_query = [
            country_counts,
            aircraft_type_counts,
            aircraft_purpose_counts,
            engine_type_counts,
            status_counts,
        ]

        query = (union_all(*union_all_query).select())

        return (await self.session.execute(query)).mappings().all()

    async def tags_list(self):
        """
        Вывод списка доступных тегов
        """

        query = (
            select(
                TagsCategories.title.label("category"),
                ArticlesTagsAssociation.tag_id.label("tag"),
            )
            .join(Tags, Tags.tag_id == ArticlesTagsAssociation.tag_id)
            .join(TagsCategories, TagsCategories.category_id == Tags.tag_category_id)
            .join(Articles, Articles.id == ArticlesTagsAssociation.article_id)
            .where(
                Articles.is_published.is_(True),
                Articles.is_archived.is_(False),
            )
            .distinct()
        )

        return (await self.session.execute(query)).mappings().all()
