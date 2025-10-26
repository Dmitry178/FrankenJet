"""
Репозиторий конструкторских бюро, приведён для примера, в текущей итерации проекта не используются.
"""

from app.db.models import DesignBureaus
from app.db.repository.base import BaseRepository


class DesignBureausRepository(BaseRepository):
    """
    Репозиторий модели конструкторских бюро
    """

    model = DesignBureaus
