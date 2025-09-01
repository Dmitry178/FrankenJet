from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.users import Users
from app.db.repository.base import BaseRepository


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
