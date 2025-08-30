from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Users(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # при использовании CITEXT установить расширение CREATE EXTENSION IF NOT EXISTS citext;
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)  # длина 254 символа согласно RFC 5321
    hashed_password: Mapped[str] = mapped_column(String(64), nullable=False)
