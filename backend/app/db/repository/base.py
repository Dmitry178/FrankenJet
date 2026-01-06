from pydantic import BaseModel
from sqlalchemy import select, exists, delete, func, update
from sqlalchemy.dialects.postgresql import insert
from typing import Type, List, Dict

from app.db import Base


class BaseEmptyRepository:
    model: Type[Base] | None = None

    def __init__(self, session):
        self.session = session


class BaseRepository:
    model: Type[Base] | None = None

    def __init__(self, session):
        self.session = session

    async def count(self, *filters, **filter_by) -> int:
        """
        Подсчёт количества строк в запросе
        """

        query = (
            select(func.count())
            .select_from(self.model)
            .filter(*filters)
            .filter_by(**filter_by)
        )

        return (await self.session.execute(query)).scalar()

    async def is_exists(self, *filters, **filter_by) -> bool:
        """
        Проверка на существование записи
        """

        '''
        # вариант только с where и *filters:
        query = select(
            exists().select_from(self.model)
            .where(*filters)
        )
        '''

        query = select(
            exists(
                select(self.model)
                .where(*filters)
                .filter_by(**filter_by)
            )
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
        Получение одной (или ни одной) записи по фильтру
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

        # подзапрос с фильтрацией и row_number()
        subquery = (
            select(
                self.model,
                func.count().over().label("total_count")  # оконная функция: count() по всем строкам результата
            )
            .filter(*filters)
            .filter_by(**filter_by)
            .subquery()
        )

        # основной запрос к подзапросу с offset и limit
        query = select(subquery)

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        rows = result.mappings().all()

        # извлечение данных и total_count
        data = []
        total_count = 0
        if rows:
            # total_count будет одинаковым для всех строк, так как это оконная функция по всем строкам
            total_count = rows[0]["total_count"]
            data = [dict(row) for row in rows]
            # удаляем "total_count" из каждой строки
            for row in data:
                del row["total_count"]

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

    async def insert_all(self, data: BaseModel | None = None, values: List[Dict] | None = None, commit=False) -> None:
        """
        Добавление массива данных
        """

        if not values and not data:
            return None

        stmt = insert(self.model).values(values) if values else insert(**data.model_dump())
        await self.session.execute(stmt)

        if commit:
            await self.session.commit()

        return None

    async def insert_all_conflict(
            self,
            data: BaseModel | None = None,
            values: List[Dict] | None = None,
            on_conflict_do_nothing=True,
            commit=False
    ) -> None:
        """
        Добавление массива данных
        """

        if not values and not data:
            return None

        stmt = insert(self.model).values(values) if values else insert(self.model).values(**data.model_dump())

        if on_conflict_do_nothing:
            stmt = stmt.on_conflict_do_nothing()
        else:
            stmt = stmt.on_conflict_do_update()

        await self.session.execute(stmt)

        if commit:
            await self.session.commit()

        return None

    async def update(
            self,
            data: BaseModel | dict | None = None,
            exclude_unset: bool = False,
            scalars=False,
            commit=False,
            *filters,
            **filter_by
    ):
        """
        Обновление данных
        """

        if isinstance(data, BaseModel):
            values = data.model_dump(by_alias=True, exclude_unset=exclude_unset)
        elif isinstance(data, dict):
            values = data
        else:
            raise ValueError("data must be a dict or a Pydantic model instance")

        stmt = (
            update(self.model)
            .values(**values)
            .filter(*filters)
            .filter_by(**filter_by)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)

        if commit:
            await self.session.commit()

        return result.scalars().one_or_none() if scalars else result.mappings().one_or_none()

    async def delete(self, commit=False, *filters, **filter_by) -> int:
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

        return result.rowcount  # количество удалённых строк
