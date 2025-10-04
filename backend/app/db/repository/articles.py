from sqlalchemy import select, func, true

from app.db.models import Articles, Aircraft
from app.db.repository.base import BaseRepository


class ArticlesRepository(BaseRepository):
    """
    Репозиторий модели статей
    """

    model = Articles

    async def select_random_articles(self, limit: int = None):
        """
        Получение случайных статей
        """

        query = (
            select(Articles.slug, Articles.title, Articles.summary, Aircraft.image_url)
            .select_from(Articles)
            .join(Aircraft, Aircraft.article_id == Articles.id)
            .where(Articles.is_published == true())
            .order_by(func.random())
            .limit(limit)
        )
        result = await self.session.execute(query)

        return result.mappings().all()
