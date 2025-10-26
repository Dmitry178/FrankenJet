from app.db.models import Aircraft
from app.db.repository.base import BaseRepository


class AircraftRepository(BaseRepository):
    """
    Репозиторий модели воздушных судов
    """

    model = Aircraft
