from app.db.models import Articles
from app.db.repository.base import BaseRepository


class ArticlesRepository(BaseRepository):
    """
    Репозиторий модели статей
    """

    model = Articles
