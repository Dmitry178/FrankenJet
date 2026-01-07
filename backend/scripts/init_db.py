# ruff: noqa: F403, F405

""" Инициализация базы данных """

import asyncio
import asyncpg
import logging
import sys

sys.path.append("/code")

from environs import Env
from urllib.parse import urlparse


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
                init_db_logger.info(f"Создана база данных {self.db_name}")
            else:
                init_db_logger.info(f"База данных {self.db_name} уже существует")

            user_exists = await conn.fetchval(f"SELECT 1 FROM pg_roles WHERE rolname='{self.db_user}'")
            if not user_exists:
                init_db_logger.info(f"Создан пользователь {self.db_user}")
                await conn.execute(f"CREATE USER {self.db_user} WITH PASSWORD '{self.db_pass}'")
            else:
                init_db_logger.info(f"Пользователь {self.db_user} уже существует")

            await conn.execute(f"GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user}")
            await conn.close()

        except asyncpg.PostgresError as ex:
            init_db_logger.error(f"Ошибка создания базы данных/пользователя: {ex}")
            sys.exit(1)

        except Exception as ex:
            init_db_logger.error(f"Ошибка при создании таблиц SQLAlchemy: {ex}")
            sys.exit(1)


async def main() -> None:
    """
    Запуск скриптов инициализации базы данных
    """

    env = Env()
    env.read_env()

    db_conn = env.str("DB_CONN")
    assert db_conn, "Строка подключения отсутствует"

    init_db_logger.info("Создание базы данных и пользователя")
    await DatabaseCreator(db_conn).create_database_and_user()

    init_db_logger.info("Инициализация базы данных завершена")
    return None


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

init_db_logger = logging.getLogger()

if __name__ == "__main__":
    asyncio.run(main())
