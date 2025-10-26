"""
Модели конструкторов, приведены для примера, в текущей итерации проекта не используются.
При использовании данных моделей необходимо раскомментировать поля, добавить модели
в /backend/app/db/models/__init__.py, и провести миграции.
"""

from datetime import date
# from typing import TYPE_CHECKING, List

from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.db.models.base import TimestampMixin
from app.db.types import uid_pk, str_32, str_128

# if TYPE_CHECKING:
#     from app.db.models import Aircraft, DesignersBureausAssociation, DesignBureaus, Countries


class Designers(Base, TimestampMixin):
    """
    Конструкторы
    """

    __tablename__ = "designers"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    # country_id: Mapped[fk_country]  # раскомментировать при использовании модели в проекте

    name: Mapped[str_32] = mapped_column(unique=True)  # имя конструктора
    original_name: Mapped[str_32 | None] = mapped_column(unique=True)  # имя на оригинальном языке
    birth_date: Mapped[date | None] = mapped_column(Date)
    death_date: Mapped[date | None] = mapped_column(Date)
    image_url: Mapped[str_128 | None]  # URL основного изображения

    '''
    # раскомментировать при использовании модели в проекте
    country: Mapped["Countries"] = relationship(back_populates="designers")
    aircraft_association: Mapped[List["AircraftDesignersAssociation"]] = relationship(
        back_populates="designer",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    aircraft: Mapped[List["Aircraft"]] = relationship(
        secondary="articles.aircraft_designers_at",
        back_populates="designers",
        viewonly=True,  # для предотвращения прямого добавления самолетов через designer.aircraft
    )
    bureau_association: Mapped[List["DesignersBureausAssociation"]] = relationship(
        back_populates="designer",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    design_bureaus: Mapped[List["DesignBureaus"]] = relationship(
        secondary="articles.designers_bureaus_at",
        back_populates="designers",
        viewonly=True,  # для предотвращения прямого добавления КБ через конструктора
    )
    '''


'''
# раскомментировать при использовании модели в проекте
class AircraftDesignersAssociation(Base):
    """
    Ассоциативная таблица для связи самолётов и конструкторов
    """

    __tablename__ = "aircraft_designers_at"
    __table_args__ = {"schema": "articles"}

    aircraft_id: Mapped[fk_aircraft] = mapped_column(ForeignKey(ondelete="CASCADE"), primary_key=True)
    designer_id: Mapped[fk_designer] = mapped_column(ForeignKey(ondelete="CASCADE"), primary_key=True)
    role: Mapped[str_64 | None]  # роли ("главный конструктор", "ведущий инженер", ...)

    aircraft: Mapped["Aircraft"] = relationship(back_populates="designers_association")
    designer: Mapped["Designers"] = relationship(back_populates="aircraft_association")
'''
