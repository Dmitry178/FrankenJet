from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from app.db.models.users import Users
from app.db.repository.base import BaseRepository
from app.schemas.users import SUserCreateOAuth2


class UsersRepository(BaseRepository):
    """
    Репозиторий пользователей
    """

    model = Users
    # mapper = UsersDataMapper  # TODO: добавить mapper

    async def get_user_with_roles(self, *filters, **filter_by):
        """
        Получение пользователя с его ролями
        """

        query = (
            select(Users)
            .filter(*filters)
            .filter_by(**filter_by)
            .options(selectinload(Users.roles))
        )

        return (await self.session.execute(query)).scalars().one_or_none()

    async def get_or_create_user(self, user_data: SUserCreateOAuth2) -> int:
        """
        Создание пользователя, либо получение пользователя, если он уже создан
        """

        '''
        Создаётся пользователь (ключевое поле - email), если он уже есть, возвращается пользователь с ролями
        '''

        # добавление пользователя
        insert_stmt = (
            insert(Users)
            .values(**user_data.model_dump())
            .on_conflict_do_nothing(index_elements=['email'])
            .returning(Users.id)
        )

        # выбор пользователя
        select_stmt = (
            select(Users.id)
            .where(Users.email == user_data.email)
        )

        # CTE
        cte = insert_stmt.cte('insert_cte')
        id_stmt = select(cte.c.id).union_all(select_stmt).cte('id_cte')

        # итоговый запрос
        query = (
            select(Users)
            .join(id_stmt, Users.id == id_stmt.c.id)  # объединение с id_cte
            .options(selectinload(Users.roles))  # добавление ролей
        )

        return (await self.session.execute(query)).scalars().one_or_none()
