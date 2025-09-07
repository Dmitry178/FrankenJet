from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING, List

from app.db import Base
from app.db.types import str_16, str_64, str_256, fk_user, fk_role

if TYPE_CHECKING:
    from app.db.models import RefreshTokens


class Users(Base):
    """
    Пользователи
    """

    __tablename__ = "users"
    __table_args__ = {"schema": "users"}

    # при использовании UUID установить расширение "uuid-ossp"
    id: Mapped[int] = mapped_column(primary_key=True)

    # при использовании CITEXT установить расширение "citext";
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)  # длина 254 символа согласно RFC 5321
    hashed_password: Mapped[str_64 | None]  # для OAuth2 поле пустое (см. документацию)
    full_name: Mapped[str_64 | None]  # полное имя
    first_name: Mapped[str_64 | None]  # имя
    last_name: Mapped[str_64 | None]  # фамилия
    picture: Mapped[str_256 | None]  # ссылка на фото профиля

    jti: Mapped[list["RefreshTokens"]] = relationship(back_populates="user")
    roles_association: Mapped[List["UsersRolesAssociation"]] = relationship(
        back_populates="user"
    )
    roles: Mapped[List["Roles"]] = relationship(
        secondary="users.users_roles_as",
        back_populates="users",
        viewonly=True
    )


class Roles(Base):
    """
    Роли пользователей
    """

    __tablename__ = "roles"
    __table_args__ = {"schema": "users"}

    role: Mapped[str_16] = mapped_column(primary_key=True)

    users_association: Mapped[List["UsersRolesAssociation"]] = relationship(
        back_populates="role"
    )
    users: Mapped[List["Users"]] = relationship(
        secondary="users.users_roles_as",
        back_populates="roles",
        viewonly=True
    )


class UsersRolesAssociation(Base):
    """
    Ассоциативная таблица для связи пользователей и ролей
    """

    __tablename__ = "users_roles_as"
    __table_args__ = (
        Index("ix_users_roles_as_user_id", "user_id"),
        Index("ix_users_roles_as_role_id", "role_id"),
        {"schema": "users"},
    )

    user_id: Mapped[fk_user] = mapped_column(primary_key=True)
    role_id: Mapped[fk_role] = mapped_column(primary_key=True)

    user: Mapped["Users"] = relationship(back_populates="roles_association")
    role: Mapped["Roles"] = relationship(back_populates="users_association")
