import json
import pytest

from httpx import AsyncClient, ASGITransport

from app.config.env import settings, AppMode
from app.core.db_manager import DBManager
from app.db import async_session_maker_null_pool, engine_null_pool, Base
from app.db.models import Articles, Aircraft
from app.dependencies.db import get_db
from main import app
from scripts.init_data import DataUtils


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.APP_MODE == AppMode.test


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> DBManager:
    async for db in get_db_null_pool():
        yield db

app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session")
async def ac() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def init_database(check_test_mode):

    print("Очистка базы данных")

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("Загрузка данных из файлов")

    with open("tests/mocks/roles.json", "r") as file:
        mock_roles = json.load(file)

    with open("tests/mocks/countries.json", "r") as file:
        mock_countries = json.load(file)

    with open("tests/mocks/articles.json", "r") as file:
        mock_articles = json.load(file)
        mock_articles = DataUtils().convert_data_types(Articles, mock_articles)

    with open("tests/mocks/aircraft.json", "r") as file:
        mock_aircraft = json.load(file)
        mock_aircraft = DataUtils().convert_data_types(Aircraft, mock_aircraft)

    with open("tests/mocks/facts.json", "r") as file:
        mock_facts = json.load(file)

    print("Добавление исходных данных")

    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.auth.roles.insert_all(values=mock_roles)
        await db_.aircraft.countries.insert_all(values=mock_countries)
        await db_.articles.insert_all(values=mock_articles)
        await db_.aircraft.aircraft.insert_all(values=mock_aircraft)
        await db_.facts.insert_all(values=mock_facts)
        await db_.commit()


@pytest.fixture(scope="session", autouse=True)
async def register_user(init_database, ac):
    response = await ac.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password",
        }
    )
    assert response.status_code == 200, "Ошибка создания пользователя"
