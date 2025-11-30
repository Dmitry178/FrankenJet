from pgvector.sqlalchemy import Vector
from sqlalchemy import Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped

from app.db import Base
from app.db.models.base import TimestampMixin


class ProjectKnowledge(Base, TimestampMixin):
    """
    База знаний о проекте
    """

    __tablename__ = "project_knowledge"
    __table_args__ = {"schema": "app"}
    '''
    __table_args__ = (
        Index(
            "idx_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_l2_ops"}
        ),
        {"schema": "app"}
    )
    '''

    id: Mapped[int] = mapped_column(primary_key=True)
    chunk: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    # embedding: Mapped[Vector] = mapped_column(Vector(384))
