from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.db.types import str_32, str_128

if TYPE_CHECKING:
    from app.db.models import Aircraft, DesignBureaus, Designers, Manufacturers


class Countries(Base):
    """
    Страны
    """

    __tablename__ = "countries"
    __table_args__ = {"schema": "articles"}

    id: Mapped[str] = mapped_column(String(2), primary_key=True)  # двухбуквенный ISO-код страны

    name: Mapped[str_32] = mapped_column(unique=True)  # название страны
    iso_code: Mapped[str | None] = mapped_column(String(3), unique=True, nullable=True)  # трёхбуквенный ISO-код страны
    flag_image_url: Mapped[str_128 | None]  # URL изображения флага страны

    aircraft: Mapped[List["Aircraft"]] = relationship(back_populates="country")
    design_bureaus: Mapped[List["DesignBureaus"]] = relationship(back_populates="country")
    designers: Mapped[List["Designers"]] = relationship(back_populates="country")
    manufacturers: Mapped[List["Manufacturers"]] = relationship(back_populates="country")
