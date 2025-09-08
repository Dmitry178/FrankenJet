from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Миксин для добавления полей created_at и updated_at
    """

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("now()"),
        onupdate=datetime.now()
    )
