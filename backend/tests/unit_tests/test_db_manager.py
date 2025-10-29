from app.core.db_manager import DBManager
from app.schemas.facts import SFacts


async def test_db_manager_rollback(db: DBManager):
    """
    Тестирование отката транзакции в DBManager
    """

    fact_to_test = "fact to test"
    is_exists = await db.facts.is_exists(fact=fact_to_test)
    assert is_exists is False

    await db.facts.insert_one(id=101, data=SFacts(fact=fact_to_test))
    await db.rollback()

    is_exists = await db.facts.is_exists(fact=fact_to_test)
    assert is_exists is False
