from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Users(Base):
    """
    Пользователи
    """

    __tablename__ = "users"

    # при использовании UUID установить расширение "uuid-ossp"
    id: Mapped[int] = mapped_column(primary_key=True)

    # при использовании CITEXT установить расширение "citext";
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)  # длина 254 символа согласно RFC 5321
    hashed_password: Mapped[str | None] = mapped_column(String(64), nullable=True)  # для OAuth2 поле пустое (см. доку)
    full_name: Mapped[str | None] = mapped_column(String(60))  # полное имя
    first_name: Mapped[str | None] = mapped_column(String(60))  # имя
    last_name: Mapped[str | None] = mapped_column(String(60))  # фамилия

    roles: Mapped[list["Roles"]] = relationship(secondary="user_roles", back_populates="users")
    # user_roles: Mapped[list["UserRoles"]] = relationship(back_populates="user")


class Roles(Base):
    """
    Роли пользователей
    """

    __tablename__ = "roles"

    role: Mapped[str] = mapped_column(String(16), primary_key=True)

    users: Mapped[list["Users"]] = relationship(secondary="user_roles", back_populates="roles")
    # user_roles: Mapped[list["UserRoles"]] = relationship(back_populates="role")


class UserRoles(Base):
    """
    Ассоциативная таблица для связи пользователей и ролей
    """

    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(ForeignKey("roles.role"), primary_key=True)

    # user: Mapped["Users"] = relationship(back_populates="user_roles")
    # role: Mapped["Roles"] = relationship(back_populates="user_roles")
