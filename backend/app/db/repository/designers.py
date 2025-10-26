"""
Репозиторий конструкторов, приведён для примера, в текущей итерации проекта не используются.
"""

from app.db.models import Designers
from app.db.repository.base import BaseRepository


class DesignersRepository(BaseRepository):
    """
    Репозиторий модели конструкторов
    """

    model = Designers
