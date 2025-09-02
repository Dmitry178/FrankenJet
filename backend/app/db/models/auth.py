import uuid

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Boolean, UUID, DateTime, text, false
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db import Base

if TYPE_CHECKING:
    from app.db.models import Users


class RefreshTokens(Base):
    """
    Refresh-токены (jti)
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    jti: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    issued_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("now()"))
    revoked: Mapped[bool] = mapped_column(Boolean, server_default=false())
    # device_info: Mapped[str | None] = mapped_column(JSONB)

    user: Mapped["Users"] = relationship(back_populates="jti")
