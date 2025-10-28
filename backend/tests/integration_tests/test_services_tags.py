import pytest

from app.core.db_manager import DBManager
from app.db.models.aircraft import AircraftTypes, EngineTypes, AircraftStatus
from app.db.models.articles import ArticleCategories
from app.services.tags import TagsServices


@pytest.mark.asyncio
async def test_auto_create_integration(db: DBManager):
    """
    Тестирование TagsServices().auto_create (автоматическая генерация тегов)
    """

    service = TagsServices(db)
    await db.tags.delete()  # удаление всех тегов
    await service.auto_create()
    tags = await service.get_tags()
    assert len(tags) > 0

    countries = [country["name"] for country in await db.countries.select_all()]
    article_categories = [ArticleCategories(item).value for item in ArticleCategories]
    aircraft_types = [AircraftTypes(item).value for item in AircraftTypes]
    engine_types = [EngineTypes(item).value for item in EngineTypes]
    aircraft_status = [AircraftStatus(item).value for item in AircraftStatus]

    expected_tags = countries + article_categories + aircraft_types + engine_types + aircraft_status
    assert tags == expected_tags
