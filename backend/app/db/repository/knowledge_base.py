from app.db.models import ProjectKnowledge
from app.db.repository.base import BaseRepository


class ProjectKnowledgeRepository(BaseRepository):
    """
    Репозиторий модели базы знаний о проекте
    """

    model = ProjectKnowledge
