from sqlalchemy import update

from app.db.models import Tags
from app.db.repository.base import BaseRepository


class TagsRepository(BaseRepository):
    """
    Репозиторий модели стран
    """

    model = Tags

    async def update_tag(self, old_value: str, new_value: str):
        """
        Редактирование тега
        """

        stmt = (
            update(self.model)
            .values(tag_id=new_value)
            .filter_by(tag_id=old_value)
        )
        await self.session.execute(stmt)
        await self.session.commit()
