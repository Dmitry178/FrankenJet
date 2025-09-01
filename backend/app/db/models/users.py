from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Users(Base):

    __tablename__ = "users"

    # при использовании UUID установить расширение "uuid-ossp"
    id: Mapped[int] = mapped_column(primary_key=True)

    # при использовании CITEXT установить расширение "citext";
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)  # длина 254 символа согласно RFC 5321
    hashed_password: Mapped[str | None] = mapped_column(String(64), nullable=True)  # для OAuth2 поле пустое (см. доку)
    full_name: Mapped[str | None] = mapped_column(String(60))  # полное имя
    first_name: Mapped[str | None] = mapped_column(String(60))  # имя
    last_name: Mapped[str | None] = mapped_column(String(60))  # фамилия


# TODO: добавить модели ролей пользователей
