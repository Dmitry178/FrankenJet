"""
Репозиторий производителей, приведён для примера, в текущей итерации проекта не используются.
"""

from app.db.models import Manufacturers
from app.db.repository.base import BaseRepository


class ManufacturersRepository(BaseRepository):
    """
    Репозиторий модели производителей
    """

    model = Manufacturers
