from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.db.types import str_256


class Facts(Base):
    """
    Модель фактов об авиации
    """

    __tablename__ = "facts"
    __table_args__ = {"schema": "articles"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fact: Mapped[str_256] = mapped_column(unique=True)  # факт об авиации
