from pydantic import BaseModel
from sqlalchemy import select, insert, exists, delete, func, over


class BaseRepository:

    model = None

    def __init__(self, session):
        self.session = session

    async def is_exists(self, *filters, **filter_by) -> bool:
        """
        Проверка на существование записи
        """

        query = select(
            exists().select_from(self.model)
            .where(*filters)
            .filter_by(**filter_by)
        )
        return (await self.session.execute(query)).scalar()

    async def select_one_or_none(self, *filters, **filter_by):
        """
        Получение записи по фильтру
        """

        query = (
            select(self.model.__table__.columns)
            .filter(*filters)
            .filter_by(**filter_by)
        )
        return (await self.session.execute(query)).mappings().one_or_none()

    async def select_all(self, *filters, **filter_by):
        """
        Получение данных из базы по фильтру
        """

        query = (
            select(self.model.__table__.columns)
            .filter(*filters)
            .filter_by(**filter_by)
        )
        return (await self.session.execute(query)).mappings().all()

    async def select_all_paginated(self, offset: int = 0, limit: int = None, *filters, **filter_by):
        """
        Получение данных из базы по фильтру с пагинацией
        """

        query = (
            select(self.model.__table__.columns)
            .filter(*filters)
            .filter_by(**filter_by)
            .offset(offset)
        )

        if limit is not None:
            query = query.limit(limit)

        return (await self.session.execute(query)).mappings().all()

    async def select_paginated_with_count(
            self, offset: int = 0, limit: int = None, *filters, **filter_by
    ):
        """
        Получение данных из базы по фильтру с пагинацией и подсчетом общего количества строк
        """

        query = (
            select(*self.model.__table__.columns,
                   func.count(over()).label("total_count"))
            .filter(*filters)
            .filter_by(**filter_by)
        )

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        rows = result.mappings().all()

        # подсчёт количества строк (всего)
        if rows:
            total_count = rows[0]['total_count']
        else:
            total_count = 0

        data = [dict(row) for row in rows]
        for row in data:
            del row['total_count']

        return data, total_count

    async def insert_data(self, **values):
        """
        Добавление данных
        """

        stmt = (
            insert(self.model)
            .values(**values)
            .returning(self.model)
        )
        return (await self.session.execute(stmt)).mappings().one()

    async def insert_model_data(self, data: BaseModel):
        """
        Добавление данных
        """

        stmt = (
            insert(self.model)
            .values(**data.model_dump())
            .returning(self.model)
        )
        return (await self.session.execute(stmt)).mappings().one()

    async def insert_model_data_scalar(self, data: BaseModel):
        """
        Добавление данных
        """

        stmt = (
            insert(self.model)
            .values(**data.model_dump())
            .returning(self.model)
        )
        return (await self.session.execute(stmt)).scalars().one()

    async def delete(self, *filters, **filter_by) -> int:
        """
        Удаление записи по фильтру
        """

        stmt = (
            delete(self.model)
            .filter(*filters)
            .filter_by(**filter_by)
        )
        return (await self.session.execute(stmt)).rowcount
