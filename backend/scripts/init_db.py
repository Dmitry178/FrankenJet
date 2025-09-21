# ruff: noqa: F403, F405

"""
Инициализация базы данных, добавление расширений и пользователя
"""

import asyncio
import asyncpg
import json
import os
import sys

sys.path.append("/code")

from alembic import command
from alembic.config import Config
from datetime import datetime
from environs import Env
from pathlib import Path
from sqlalchemy import DDL, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from typing import TypeVar, Type
from urllib.parse import urlparse

from app.core.logs import logger
from app.db import Base
from app.db.models import *
from app.services.security import SecurityService

T = TypeVar("T", bound=Base)

# путь к статьям
BASE_ARTICLES_PATH = "./scripts/articles"

# расширения базы данных для установки
extensions = [
    # "citext",
    "uuid-ossp",
]

# схемы базы данных
schemas = [
    "articles",
    "users"
]


class DatabaseCreator:
    """
    Создание БД и пользователя, назначение привилегий
    """

    def __init__(self, db_conn: str):

        url = urlparse(f"postgresql://{db_conn}")
        self.db_user = url.username
        self.db_pass = url.password
        self.db_host = url.hostname
        self.db_port = url.port
        self.db_name = url.path[1:]
        self.db_conn = f"postgresql+asyncpg://{db_conn}"

    async def create_database_and_user(self):
        """
        Создание базы данных и пользователя, если они не существуют
        """

        try:
            conn = await asyncpg.connect(
                user=self.db_user,
                password=self.db_pass,
                host=self.db_host,
                port=self.db_port,
                database="postgres",  # база данных по умолчанию
            )

            db_exists = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname='{self.db_name}'")
            if not db_exists:
                await conn.execute(f"CREATE DATABASE {self.db_name}")
                logger.info(f"Создана база данных {self.db_name}")
            else:
                logger.info(f"База данных {self.db_name} уже существует")

            user_exists = await conn.fetchval(f"SELECT 1 FROM pg_roles WHERE rolname='{self.db_user}'")
            if not user_exists:
                logger.info(f"Создан пользователь {self.db_user}")
                await conn.execute(f"CREATE USER {self.db_user} WITH PASSWORD '{self.db_pass}'")
            else:
                logger.info(f"Пользователь {self.db_user} уже существует")

            await conn.execute(f"GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user}")

            await conn.close()

        except asyncpg.PostgresError as ex:
            logger.error(f"Ошибка создания базы данных/пользователя: {ex}")
            sys.exit(1)

        except Exception as ex:
            logger.error(f"Ошибка при создании таблиц SQLAlchemy: {ex}")
            sys.exit(1)


class DatabaseHandler:
    """
    Запуск миграций, добавление первичных данных
    """

    def __init__(self, db_conn: str, admin_user: str | None = None, admin_pass: str | None = None):

        async_database_url = f"postgresql+asyncpg://{db_conn}"
        self.db_conn = db_conn
        self.async_engine = create_async_engine(url=async_database_url, echo=False)
        self.async_session_maker = async_sessionmaker(bind=self.async_engine)
        self.session = None

        # True - создание таблиц через миграции Alembic, False - создание таблиц через Base.metadata.create_all
        self.run_migrations = False

        if admin_user and admin_pass:
            self.admin_user = admin_user
            self.admin_pass = SecurityService().hash_password(admin_pass)
        else:
            self.admin_user = None
            self.admin_pass = None

    async def __aenter__(self):
        """
        Асинхронный context-manager для создания сессии
        """

        self.session = self.async_session_maker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Асинхронный context manager для закрытия сессии
        """

        if exc_type is not None:
            await self.session.rollback()
        await self.session.close()

    async def create_tables(self) -> None:
        """
        Создание таблиц базы данных
        """

        async with self.async_engine.begin() as conn:

            # создание расширений
            for extension in extensions:
                await conn.execute(DDL(f"CREATE EXTENSION IF NOT EXISTS \"{extension}\""))

            # создание схем
            for schema in schemas:
                await conn.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

            if self.run_migrations:
                # TODO: исправить миграции
                alembic_cfg = Config("/code/alembic.ini", ini_section="alembic.local")
                raw_connection = await conn.get_raw_connection()
                alembic_cfg.attributes["connection"] = raw_connection.connection
                command.upgrade(alembic_cfg, "head")
                logger.info("Миграции завершены")
            else:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Схемы и таблицы созданы")

        return None

    async def insert_countries(self) -> None:
        """
        Заполнение таблицы стран
        """

        countries = [
            {"id": "ru", "name": "Россия", "iso_code": "RUS"},
            {"id": "su", "name": "СССР", "iso_code": None},
            {"id": "us", "name": "США", "iso_code": "USA"},
            {"id": "de", "name": "Германия", "iso_code": "GER"},
            {"id": "fr", "name": "Франция", "iso_code": "FRA"},
        ]

        stmt = insert(Countries).values(countries).on_conflict_do_nothing()
        await self.session.execute(stmt)
        await self.session.commit()

        logger.info("Таблица стран заполнена")

        return None

    async def insert_roles(self) -> None:
        """
        Заполнение таблицы ролей пользователей
        """

        roles = [
            {"role": "admin"},  # админская роль
            {"role": "demo"},  # админская роль с правами read only
            {"role": "editor"},  # редактор карточек с данными
            {"role": "moderator"},  # модератор комментариев
        ]

        stmt = insert(Roles).values(roles).on_conflict_do_nothing()
        await self.session.execute(stmt)
        await self.session.commit()

        logger.info("Таблица ролей заполнена")

        return None

    async def insert_users(self) -> None:
        """
        Заполнение таблицы пользователей
        """

        if not self.admin_user or not self.admin_pass:
            return

        # добавление пользователя
        query = await self.session.execute(select(Users.id).where(Users.email == self.admin_user))
        user_id = query.scalar_one_or_none()

        if not user_id:
            stmt = insert(Users).values(email=self.admin_user, hashed_password=self.admin_pass).returning(Users.id)
            user_id = (await self.session.execute(stmt)).scalar()
            logger.info("Пользователь создан")

        # добавление роли пользователя
        query = await self.session.execute(
            select(UsersRolesAssociation).where(
                UsersRolesAssociation.user_id == user_id,
                UsersRolesAssociation.role_id == "admin"
            )
        )
        existing_role = query.scalar_one_or_none()

        if not existing_role:
            stmt = insert(UsersRolesAssociation).values(user_id=user_id, role_id="admin")
            await self.session.execute(stmt)
            logger.info("Роль пользователя назначена")

        await self.session.commit()

        return None

    async def add_data(self, model: Type[T], data: list) -> None:
        """
        Добавление данных в таблицу
        """

        if not data:
            return None

        stmt = insert(model).values(data).on_conflict_do_nothing()
        await self.session.execute(stmt)
        await self.session.commit()

        logger.info(f"Данные добавлены в {model.__name__}")

        return None


async def main() -> None:
    """
    Запуск скриптов инициализации данных
    """

    async def read_json(path: str, is_article=False) -> list:
        """
        Сборка json из файлов
        """

        directory = Path(f"{os.getcwd()}/{path}")

        # чтение списка файлов с расширением json
        files = [file.name for file in directory.glob("*.json")]

        result = []
        for file_name in files:
            file_path = directory / file_name

            # чтение json-файла
            with open(file_path, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)

                # дополнительная обработка статей
                if is_article:
                    # присоединение контента
                    content_path = directory / json_data.get("content")
                    with open(content_path, "r", encoding="utf-8") as content_file:
                        content_data = content_file.read()
                        json_data["content"] = content_data  # добавление контента

                    # указание даты публикации
                    if json_data.get("is_published"):
                        json_data["published_at"] = datetime.now()

                result.append(json_data)

        return result

    env = Env()
    env.read_env()

    db_conn = env.str("DB_CONN")
    if not db_conn:
        logger.error("Строка подключения отсутствует")
        sys.exit(1)

    admin_user = env.str("ADMIN_USER", None)
    admin_pass = env.str("ADMIN_PASS", None)

    args = sys.argv
    skip_create_db = "skip-create-db" in args
    skip_create_tables = "skip-create-tables" in args

    if not skip_create_db:
        logger.info("Создание базы данных и пользователя")
        db_creator = DatabaseCreator(db_conn)
        await db_creator.create_database_and_user()

    async with DatabaseHandler(db_conn, admin_user, admin_pass) as db_handler:

        if not skip_create_tables:
            logger.info("Миграции")
            await db_handler.create_tables()

        logger.info("Заполнение базы первичными данными")
        await db_handler.insert_roles()
        await db_handler.insert_users()
        await db_handler.insert_countries()

        logger.info("Добавление статей")
        data = await read_json(BASE_ARTICLES_PATH, is_article=True)
        await db_handler.add_data(Articles, data)

        logger.info("Добавление карточек воздушных судов")
        data = await read_json(f"{BASE_ARTICLES_PATH}/aircraft")
        await db_handler.add_data(Aircraft, data)

    return None


if __name__ == "__main__":
    asyncio.run(main())
