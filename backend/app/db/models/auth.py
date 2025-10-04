from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db import Base
from app.db.types import fk_user, uid, bool_false, datetime_now, str_256

if TYPE_CHECKING:
    from app.db.models import Users


class RefreshTokens(Base):
    """
    Refresh-токены (jti)
    """

    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "users"}
    # __table_args__ = {"schema": "auth"}

    '''
    При масштабировании проекта и подключения микросервисов, которые работают с данной моделью,
    следует перенести в отдельную схему "auth" (для безопасности и снижения накладных расходов при работе с данными)
    '''

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[fk_user]
    jti: Mapped[uid]
    issued_at: Mapped[datetime_now]
    revoked: Mapped[bool_false]
    user_agent: Mapped[str_256 | None]

    user: Mapped["Users"] = relationship(back_populates="jti")
