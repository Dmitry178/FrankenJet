from datetime import date
from typing import TYPE_CHECKING, List

from sqlalchemy import Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.db.models.base import TimestampMixin
from app.db.types import uid_pk, fk_country, str_32, str_128, fk_aircraft, fk_designer, str_64

if TYPE_CHECKING:
    from app.db.models import Aircraft, DesignersBureausAssociation, DesignBureaus, Countries


class Designers(Base, TimestampMixin):
    """
    Конструкторы
    """

    __tablename__ = "designers"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    country_id: Mapped[fk_country]

    name: Mapped[str_32] = mapped_column(unique=True)  # имя конструктора
    original_name: Mapped[str_32 | None] = mapped_column(unique=True)  # имя на оригинальном языке
    birth_date: Mapped[date | None] = mapped_column(Date)
    death_date: Mapped[date | None] = mapped_column(Date)
    known_for: Mapped[str | None] = mapped_column(Text)  # чем знаменит конструктор
    biography: Mapped[str] = mapped_column(Text)  # биография
    image_url: Mapped[str_128 | None]  # URL основного изображения

    country: Mapped["Countries"] = relationship(back_populates="designers")
    aircraft_association: Mapped[List["AircraftDesignersAssociation"]] = relationship(
        back_populates="designer"
    )
    aircraft: Mapped[List["Aircraft"]] = relationship(
        secondary="articles.aircraft_designers_as",
        back_populates="designers",
        viewonly=True,  # для предотвращения прямого добавления самолетов через designer.aircraft
    )
    bureau_association: Mapped[List["DesignersBureausAssociation"]] = relationship(
        back_populates="designer"
    )
    design_bureaus: Mapped[List["DesignBureaus"]] = relationship(
        secondary="articles.designers_bureaus_as",
        back_populates="designers",
        viewonly=True,  # для предотвращения прямого добавления КБ через конструктора
    )


class AircraftDesignersAssociation(Base):
    """
    Ассоциативная таблица для связи самолётов и конструкторов
    """

    __tablename__ = "aircraft_designers_as"
    __table_args__ = {"schema": "articles"}

    aircraft_id: Mapped[fk_aircraft] = mapped_column(primary_key=True)
    designer_id: Mapped[fk_designer] = mapped_column(primary_key=True)
    role: Mapped[str_64 | None]  # роли ("главный конструктор", "ведущий инженер", ...)

    aircraft: Mapped["Aircraft"] = relationship(back_populates="designers_association")
    designer: Mapped["Designers"] = relationship(back_populates="aircraft_association")
