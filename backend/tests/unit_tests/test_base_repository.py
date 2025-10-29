import pytest

from app.core.db_manager import DBManager
from app.db.models import Tags, Facts
from app.schemas.facts import SFacts


@pytest.mark.asyncio
async def test_base_repository(db: DBManager):
    """
    Тестирование базового репозитория
    """

    expected_tag = "tag"
    expected_fact = "fact"

    # тестирование insert_all с value=None
    result = await db.tags.insert_all(values=None)
    assert result is None

    # тестирование insert_one (проверка ниже)
    await db.tags.insert_one(tag_id=expected_tag, commit=True)

    # тестирование is_exists и за одно проверяется insert_one
    is_exists = await db.tags.is_exists(Tags.tag_id == expected_tag)
    assert is_exists is True
    is_exists = await db.tags.is_exists(tag_id=expected_tag)
    assert is_exists is True

    # тестирование select_one
    tag = await db.tags.select_one(tag_id=expected_tag)
    assert tag.get("tag_id") == expected_tag

    # тестирование select_one_or_none
    tag = await db.tags.select_one_or_none(tag_id=f"{expected_tag}1")
    assert tag is None

    # тестирование update
    # пояснение: id задаётся вручную, потому как в тестовой базе при mock данных через массовые операции,
    # в отличие от миграций, не срабатывает autoincrement, и данный код выдаёт ошибку уникального значения id
    fact_id = 100
    fact: Facts = await db.facts.insert_one(id=fact_id, fact=f"{expected_fact}1", scalars=True, commit=True)
    assert fact is not None
    assert fact.id == fact_id
    assert fact.fact == f"{expected_fact}1"

    updated_fact = SFacts(fact=expected_fact)
    fact: Facts = await db.facts.update(id=fact_id, data=updated_fact, scalars=True, commit=True)
    assert fact.fact == expected_fact

    # тестирование delete
    rows = await db.facts.delete(id=fact_id, commit=True)
    assert rows == 1

    # тестирование select_random
    result = await db.facts.select_random(columns=["fact"], limit=1)
    assert len(result) == 1

    # тестирование count и select_paginated_with_count
    limit = 3
    count = await db.facts.count()
    result, total_count = await db.facts.select_paginated_with_count(offset=1, limit=limit)
    assert len(result) == limit
    assert total_count == count
