from app.db.models import Roles
from app.db.repository.base import BaseRepository


class RolesRepository(BaseRepository):
    """
    Репозиторий ролей пользователей
    """

    model = Roles
