"""
Модели производителей, приведены для примера, в текущей итерации проекта не используются.
При использовании данных моделей необходимо раскомментировать поля, добавить модели
в /backend/app/db/models/__init__.py, и провести миграции.
"""

from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.db.models.base import TimestampMixin
from app.db.types import uid_pk, str_32

# if TYPE_CHECKING:
#     from app.db.models import Aircraft, Countries


class Manufacturers(Base, TimestampMixin):
    """
    Производители воздушных судов
    """

    __tablename__ = "manufacturers"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    # country_id: Mapped[fk_country]  # раскомментировать при использовании модели в проекте

    name: Mapped[str_32] = mapped_column(unique=True)  # название производителя
    original_name: Mapped[str_32 | None] = mapped_column(unique=True)  # название на оригинальном языке

    '''
    # раскомментировать при использовании модели в проекте
    country: Mapped["Countries"] = relationship(back_populates="manufacturers")
    aircraft_association: Mapped[List["AircraftManufacturersAssociation"]] = relationship(
        back_populates="manufacturer",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    aircraft: Mapped[List["Aircraft"]] = relationship(
        secondary="articles.aircraft_manufacturers_at",
        back_populates="manufacturers",
        viewonly=True,
    )
    '''


'''
# раскомментировать при использовании модели в проекте
class AircraftManufacturersAssociation(Base):
    """
    Ассоциативная таблица для связи самолетов и производителей
    """

    __tablename__ = "aircraft_manufacturers_at"
    __table_args__ = {"schema": "articles"}

    aircraft_id: Mapped[fk_aircraft] = mapped_column(ForeignKey(ondelete="CASCADE"), primary_key=True)
    manufacturer_id: Mapped[fk_manufacturer] = mapped_column(ForeignKey(ondelete="CASCADE"), primary_key=True)
    start_production: Mapped[date | None]  # дата начала производства на данном предприятии
    end_production: Mapped[date | None]  # дата окончания производства на данном предприятии

    aircraft: Mapped["Aircraft"] = relationship(back_populates="manufacturer_association")
    manufacturer: Mapped["Manufacturers"] = relationship(back_populates="aircraft_association")
'''
