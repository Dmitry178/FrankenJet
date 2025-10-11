from pydantic import BaseModel
from sqlalchemy import select, insert, exists, delete, func, over, update
from typing import Type, List, Dict

from app.db import Base


class BaseRepository:

    model: Type[Base] | None = None

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

    async def select_one(self, scalars=False, *filters, **filter_by):
        """
        Получение записи по фильтру
        """

        query = (
            select(self.model.__table__.columns)
            .filter(*filters)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)

        return result.scalars().one() if scalars else result.mappings().one()

    async def select_one_or_none(self, scalars=False, *filters, **filter_by):
        """
        Получение записи по фильтру
        """

        query = (
            select(self.model.__table__.columns)
            .filter(*filters)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)

        return result.scalars().one_or_none() if scalars else result.mappings().one_or_none()

    async def select_all(self, scalars=False, *filters, **filter_by):
        """
        Получение данных из базы по фильтру
        """

        query = (
            select(self.model.__table__.columns)
            .filter(*filters)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)

        return result.scalars().all() if scalars else result.mappings().all()

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
            select(*self.model.__table__.columns, func.count(over()).label("total_count"))  # noqa
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

    async def select_random(self, columns=None, scalars=False, limit: int = None, *filters, **filter_by):
        """
        Получение случайных данных
        """

        if columns is None:
            columns_to_select = [self.model.__table__.columns]
        else:
            columns_to_select = [getattr(self.model, col) for col in columns]

        query = (
            select(*columns_to_select)
            .filter(*filters)
            .filter_by(**filter_by)
            .order_by(func.random())
            .limit(limit)
        )
        result = await self.session.execute(query)

        return result.scalars().all() if scalars else result.mappings().all()

    async def insert_one(self, data: BaseModel | None = None, scalars=False, commit=False, **values):
        """
        Добавление данных
        """

        stmt = (
            insert(self.model)
            .values(**values)
            .returning(self.model)
        )
        if data:
            stmt = stmt.values(**data.model_dump(), **values)

        result = await self.session.execute(stmt)

        if commit:
            await self.session.commit()

        return result.scalars().one() if scalars else result.mappings().one()

    async def insert_bulk(self, data: BaseModel | None = None, values: List[Dict] | None = None, commit=False) -> None:
        """
        Добавление массива данных
        """

        if not values and not data:
            return

        stmt = insert(self.model).values(values) if values else insert(**data.model_dump())
        await self.session.execute(stmt)

        if commit:
            await self.session.commit()

        return None

    async def update_one(
            self,
            data: BaseModel | None = None,
            exclude_unset: bool = False,
            scalars=False,
            commit=False,
            *filters, **filter_by
    ):
        """
        Обновление данных
        """

        stmt = (
            update(self.model)
            .values(**data.model_dump(by_alias=True, exclude_unset=exclude_unset))
            .filter(*filters)
            .filter_by(**filter_by)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)

        if commit:
            await self.session.commit()

        return result.scalars().one() if scalars else result.mappings().one()

    async def delete_one(self, commit=False, *filters, **filter_by) -> int:
        """
        Удаление данных
        """

        stmt = (
            delete(self.model)
            .filter(*filters)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(stmt)

        if commit:
            await self.session.commit()

        return result.rowcount
