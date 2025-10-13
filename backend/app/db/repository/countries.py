from app.db.models import Countries
from app.db.repository.base import BaseRepository


class CountriesRepository(BaseRepository):
    """
    Репозиторий модели стран
    """

    model = Countries
