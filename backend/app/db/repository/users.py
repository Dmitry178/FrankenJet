from app.db.models.users import Users
from app.db.repository.base import BaseRepository


class UsersRepository(BaseRepository):
    """
    Репозиторий пользователей
    """

    model = Users
    # mapper = UsersDataMapper  # TODO: добавить mapper
