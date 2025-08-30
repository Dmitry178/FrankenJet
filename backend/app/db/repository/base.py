from pydantic import BaseModel
from sqlalchemy import select, insert, exists


class BaseRepository:

    model = None
    # mapper: DataMapper = None  # TODO: добавить DataMapper

    def __init__(self, session):
        self.session = session

    async def is_exists(self, *filters, **filter_by) -> bool:
        """
        Проверка на существование записи
        """

        query = select(
            exists().select_from(self.model)
            .where(*filters)
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
