"""
Модели конструкторских бюро, приведены для примера, в текущей итерации проекта не используются.
При использовании данных моделей необходимо раскомментировать поля, добавить модели
в /backend/app/db/models/__init__.py, и провести миграции.
"""

from sqlalchemy.orm import Mapped, mapped_column
# from typing import List

from app.db import Base
from app.db.models.base import TimestampMixin
from app.db.types import uid_pk, str_32, str_128, str_256

# if TYPE_CHECKING:
#     from app.db.models import Countries, Designers


class DesignBureaus(Base, TimestampMixin):
    """
    Конструкторское бюро
    """

    __tablename__ = "design_bureaus"
    __table_args__ = {"schema": "articles"}

    id: Mapped[uid_pk]
    # country_id: Mapped[fk_country]  # раскомментировать при использовании модели в проекте

    name: Mapped[str_32] = mapped_column(unique=True)  # название конструкторского бюро
    original_name: Mapped[str_32 | None] = mapped_column(unique=True)  # название на оригинальном языке
    image_url: Mapped[str_128 | None]  # логотип
    location: Mapped[str_256 | None]  # место расположения / адрес

    '''
    # раскомментировать при использовании модели в проекте
    country: Mapped["Countries"] = relationship(back_populates="design_bureaus")
    designers_association: Mapped[List["DesignersBureausAssociation"]] = relationship(
        back_populates="design_bureau",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    designers: Mapped[List["Designers"]] = relationship(
        secondary="articles.designers_bureaus_at",
        back_populates="design_bureaus",
        viewonly=True,
    )
    '''


'''
# раскомментировать при использовании модели в проекте
class DesignersBureausAssociation(Base):
    """
    Ассоциативная таблица для связи конструкторов и конструкторских бюро
    """

    __tablename__ = "designers_bureaus_at"
    __table_args__ = {"schema": "articles"}

    designer_id: Mapped[fk_designer] = mapped_column(ForeignKey(ondelete="CASCADE"), primary_key=True)
    design_bureau_id: Mapped[fk_design_bureau] = mapped_column(ForeignKey(ondelete="CASCADE"), primary_key=True)
    role: Mapped[str_64 | None]  # роль конструктора в бюро ("руководитель отдела", ...)

    designer: Mapped["Designers"] = relationship(back_populates="bureau_association")
    design_bureau: Mapped["DesignBureaus"] = relationship(back_populates="designers_association")
'''
