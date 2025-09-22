from app.db.models.articles import Facts
from app.db.repository.base import BaseRepository


class FactsRepository(BaseRepository):
    """
    Репозиторий модели фактов об авиации
    """

    model = Facts
