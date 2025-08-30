from pydantic import EmailStr
from sqlalchemy import select

from app.db.models.users import Users
from app.db.repository.base import BaseRepository


class UsersRepository(BaseRepository):
    """
    Репозиторий пользователей
    """

    model = Users
    # mapper = UserDataMapper  # TODO: добавить mapper

    async def get_user_with_hashed_password(self, email: EmailStr):
        """
        Получить запись пользователя
        """

        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        user = result.scalars().one()

        # return UserWithHashedPassword.model_validate(user)
        return user
