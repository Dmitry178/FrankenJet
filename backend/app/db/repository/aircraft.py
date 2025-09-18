from app.db.models import Aircraft, Countries, Designers
from app.db.models.aircraft import Manufacturers, DesignBureaus
from app.db.repository.base import BaseRepository


class CountriesRepository(BaseRepository):
    """
    Репозиторий модели стран
    """

    model = Countries


class AircraftRepository(BaseRepository):
    """
    Репозиторий модели воздушных судов
    """

    model = Aircraft


class DesignersRepository(BaseRepository):
    """
    Репозиторий модели конструкторов
    """

    model = Designers


class ManufacturersRepository(BaseRepository):
    """
    Репозиторий модели производителей
    """

    model = Manufacturers


class DesignBureausRepository(BaseRepository):
    """
    Репозиторий модели конструкторских бюро
    """

    model = DesignBureaus
