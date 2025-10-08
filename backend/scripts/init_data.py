# ruff: noqa: F403, F405

"""
Добавление расширений, инициализация данных
"""

import asyncio
import json
import os
import sys

sys.path.append("/code")

from alembic import command
from alembic.config import Config

from datetime import datetime, date
from environs import Env
from pathlib import Path
from pydantic import BaseModel

from sqlalchemy import DDL, select, inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from typing import TypeVar, Type
from urllib.parse import urlparse
from uuid import UUID

from app.config.app import BUCKET_IMAGES
from app.core.logs import logger
from app.core.s3_manager import S3Manager
from app.db import Base
from app.db.models import *
from app.services.security import SecurityService

T = TypeVar("T", bound=Base)

# путь к статьям
BASE_ARTICLES_PATH = "./scripts/articles"

# расширения базы данных для установки,
# выполняется sql-запрос: CREATE EXTENSION IF NOT EXISTS {extension}
extensions = [
    # "citext",
    "uuid-ossp",
]

# схемы базы данных,
# выполняется sql-запрос: CREATE SCHEMA IF NOT EXISTS {schema}
schemas = [
    "articles",
    "users"
]


class SUserCreds(BaseModel):
    """
    Схема регистрационных данных пользователя
    """

    username: str
    password: str
    roles: list[str] | None = None


class SS3Creds(BaseModel):
    """
    Схема данных подключения к S3
    """

    access_key_id: str
    secret_access_key: str
    endpoint_url: str


class DataCreator:
    """
    Запуск миграций, добавление первичных данных
    """

    def __init__(self, db_conn: str):

        async_database_url = f"postgresql+asyncpg://{db_conn}"
        parsed_db_conn = urlparse(async_database_url)

        self.db_conn = db_conn
        self.db_user = parsed_db_conn.username
        self.async_engine = create_async_engine(url=async_database_url, echo=False)
        self.async_session_maker = async_sessionmaker(bind=self.async_engine)
        self.session = None

        # True - создание таблиц через миграции Alembic, False - создание таблиц через Base.metadata.create_all
        self.run_migrations = False

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
                await conn.execute(DDL(f'CREATE EXTENSION IF NOT EXISTS "{extension}"'))

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

    async def insert_users(self, users: list[SUserCreds] | None = None) -> None:
        """
        Заполнение таблицы пользователей
        """

        if not users:
            return

        for user in users:
            # получение данных пользователя
            query = await self.session.execute(select(Users.id).where(Users.email == user.username))
            user_id = query.scalar_one_or_none()

            # добавление пользователя, если его нет в базе
            if not user_id:
                hashed_password = SecurityService().hash_password(user.password)
                stmt = (
                    insert(Users)
                    .values(
                        email=user.username, hashed_password=hashed_password
                    )
                    .returning(Users.id)
                )
                user_id = (await self.session.execute(stmt)).scalar()
                logger.info("Пользователь создан")

            # добавление ролей пользователя
            if not user.roles:
                continue

            user_roles = [{"user_id": user_id, "role_id": role} for role in user.roles]
            stmt = insert(UsersRolesAssociation).values(user_roles).on_conflict_do_nothing()
            await self.session.execute(stmt)

        await self.session.commit()

        return None

    @staticmethod
    def safe_parse_date(value: str) -> date | None:
        """
        Конвертация строк в даты, поддерживаются неполные даты (год и год-месяц)
        """

        if not value:
            return None

        try:
            # полная дата
            return date.fromisoformat(value)

        except ValueError:
            # только год
            if len(value) == 4 and value.isdigit():
                return date(int(value), 1, 1)

            # год-месяц
            if len(value) == 7 and value[4] == '-':
                year, month = value.split('-')
                if year.isdigit() and month.isdigit():
                    return date(int(year), int(month), 1)

        return None

    def convert_data_types(self, model, data: list[dict]) -> list[dict]:
        """
        Замена типов данных в строковом представлении на соответствующие типы в моделях базы (datetime.date и UUID)
        """

        mapper = inspect(model)

        # поля типа datetime.date
        date_columns = {
            col.key for col in mapper.columns
            if col.type.python_type is date
        }

        # поля типа UUID
        uuid_columns = {
            col.key for col in mapper.columns
            if col.type.python_type is UUID
        }

        # nullable-поля
        nullable_columns = {
            col.key for col in mapper.columns
            if col.nullable
        }

        # конвертация типов данных
        for row in data:
            for key, value in row.items():
                try:
                    # обработка полей типа datetime.date
                    if key in date_columns and isinstance(value, str):
                        row[key] = self.safe_parse_date(value)

                    # обработка полей типа UUID
                    elif key in uuid_columns and isinstance(value, str):
                        if value:
                            # строка не пустая
                            row[key] = UUID(value)
                        else:
                            # строка пустая
                            if key in nullable_columns:
                                # строка nullable
                                row[key] = None
                            else:
                                # строка не nullable
                                raise ValueError

                except (ValueError, AttributeError):
                    # входящие данные не соответствуют структуре базы данных
                    raise Exception

        return data

    async def add_data(self, model: Type[T], data: list[dict]) -> None:
        """
        Добавление данных в таблицу
        """

        if not data:
            return None

        # замена дат в строковом представлении на datetime.data
        data = self.convert_data_types(model, data)

        stmt = insert(model).values(data).on_conflict_do_nothing()
        await self.session.execute(stmt)
        await self.session.commit()

        logger.info(f"Данные добавлены в {model.__name__}")

        return None


async def main() -> None:
    """
    Запуск скриптов инициализации данных
    """

    async def read_json(path: str, is_article=False, has_image=False, s3manager=None) -> list[dict]:
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

                # дополнительная обработка фотографий
                if has_image and s3manager and (image_name := json_data.get("image_url")):
                    image_path = directory / image_name
                    s3_key = "/aircraft/" + str(image_name).lstrip('_').replace("_", "-")
                    if await s3manager.upload_file(BUCKET_IMAGES, image_path, s3_key=s3_key):
                        json_data["image_url"] = f"/{BUCKET_IMAGES}{s3_key}"
                    else:
                        json_data["image_url"] = None  # ошибка загрузки изображения в S3

                result.append(json_data)

        return result

    async def read_text(file: str) -> list:
        """
        Получение списка из текстового файла
        """

        file_path = Path(f"{os.getcwd()}/{file}")
        with open(file_path, "r", encoding="utf-8") as f:
            file_data = [line.strip() for line in f if line.strip()]
            return file_data

    env = Env()
    env.read_env()

    db_conn = env.str("DB_CONN")
    if not db_conn:
        logger.error("Строка подключения отсутствует")
        sys.exit(1)

    # логин/пароль админа по умолчанию
    admin_user = env.str("ADMIN_USER", None)
    admin_pass = env.str("ADMIN_PASS", None)

    users = None
    if admin_user and admin_pass:
        users = [SUserCreds(username=admin_user, password=admin_pass, roles=["admin"])]

    # создание экземпляра S3-менеджера
    access_key_id = env.str("S3_ACCESS_KEY_ID", None)
    secret_access_key = env.str("S3_SECRET_ACCESS_KEY", None)
    endpoint_url = env.str("S3_ENDPOINT_URL", None)

    s3_manager = None
    if access_key_id and secret_access_key and endpoint_url:
        s3_manager = S3Manager(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            endpoint_url=endpoint_url
        )

    # чтение аргументов скрипта
    args = sys.argv
    skip_migrations = "skip-migrations" in args

    async with DataCreator(db_conn) as db_handler:

        if not skip_migrations:
            logger.info("Миграции" if db_handler.run_migrations else "Создание таблиц")
            await db_handler.create_tables()

        logger.info("Заполнение базы первичными данными")
        await db_handler.insert_roles()
        await db_handler.insert_users(users)
        await db_handler.insert_countries()

        logger.info("Добавление фактов")
        facts = await read_text("/scripts/facts/facts.txt")
        data = [{"fact": fact} for fact in facts]
        await db_handler.add_data(Facts, data)

        logger.info("Добавление статей")
        data = await read_json(BASE_ARTICLES_PATH, is_article=True)
        await db_handler.add_data(Articles, data)

        logger.info("Добавление карточек воздушных судов")
        data = await read_json(f"{BASE_ARTICLES_PATH}/aircraft", has_image=True, s3manager=s3_manager)
        await db_handler.add_data(Aircraft, data)

    logger.info("Добавление данных завершено")


if __name__ == "__main__":
    asyncio.run(main())
