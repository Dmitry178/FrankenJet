from app.db.models import Roles, UsersRolesAssociation
from app.db.repository.base import BaseRepository


class RolesRepository(BaseRepository):
    """
    Репозиторий ролей пользователей
    """

    model = Roles


class UserRolesRepository(BaseRepository):
    """
    Репозиторий ассоциативной таблицы ролей пользователей
    """

    model = UsersRolesAssociation
