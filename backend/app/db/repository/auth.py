from app.db.models import RefreshTokens
from app.db.repository.base import BaseRepository


class RefreshTokensRepository(BaseRepository):
    """
    Репозиторий модели refresh-токенов
    """

    model = RefreshTokens
