from app.core.db_manager import DBManager
from app.db.models.aircraft import AircraftTypes, EngineTypes, AircraftStatus
from app.db.models.articles import ArticleCategories
from app.decorators.db_errors import handle_basic_db_errors
from app.schemas.tags import STags


class TagsServices:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @handle_basic_db_errors
    async def auto_create(self) -> None:
        """
        Автоматическое создание тегов (из стран, категорий статей, типов сущностей приложения, и т.д.)
        """

        # сбор данных
        countries = [country["name"] for country in await self.db.countries.select_all()]
        article_categories = [ArticleCategories(item).value for item in ArticleCategories]
        aircraft_types = [AircraftTypes(item).value for item in AircraftTypes]
        engine_types = [EngineTypes(item).value for item in EngineTypes]
        aircraft_status = [AircraftStatus(item).value for item in AircraftStatus]

        # суммирование
        tags = countries + article_categories + aircraft_types + engine_types + aircraft_status

        # текущие теги в базе
        current_tags = [tag["tag_id"].lower() for tag in await self.db.tags.select_all()]

        # фильтрация тегов
        tags_to_add = [tag for tag in tags if tag.lower() not in current_tags]

        # формирование списка тегов и добавление в базу
        tags_to_add = [{"tag_id": tag} for tag in tags_to_add]
        await self.db.tags.insert_all(values=tags_to_add, commit=True)

        return None

    @handle_basic_db_errors
    async def get_tags(self):
        """
        Получение списка тегов
        """

        tags = await self.db.tags.select_all()
        return [tag["tag_id"] for tag in tags]

    @handle_basic_db_errors
    async def add_tag(self, tag: str):
        """
        Добавление тега
        """

        return await self.db.tags.insert_one(STags(tag_id=tag), commit=True)

    @handle_basic_db_errors
    async def edit_tag(self, old_value: str, new_value: str):
        """
        Редактирование тега
        """

        return await self.db.tags.update_tag(old_value, new_value)

    @handle_basic_db_errors
    async def delete_tag(self, tag: str):
        """
        Удаление тега
        """

        return await self.db.tags.delete(tag_id=tag, commit=True)

    @handle_basic_db_errors
    async def count_tags(self):
        """
        Подсчёт количества тегов в статьях
        """

        result = await self.db.tags.count_tags()
        return [dict(row) for row in result]
