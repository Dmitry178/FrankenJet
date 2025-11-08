from enum import Enum

from app.config.env import settings
from app.core.db_manager import DBManager
from app.db.models.aircraft import AircraftTypes, EngineTypes, AircraftStatus, AircraftPurpose
from app.decorators.db_errors import handle_basic_db_errors


class PagesService:

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        self.db = db

    @handle_basic_db_errors
    async def home(self) -> dict:
        """
        Информация для главной страницы
        """

        context = {}

        # случайные статьи
        random_articles = await self.db.articles.get_random_articles(limit=3) or []

        # обработка изображений
        processed_articles = [
            {
                **article,
                "image_url": f"{settings.S3_DIRECT_URL}{article['image_url']}" if article["image_url"] else None
            }
            for article in random_articles
        ]

        # случайные факты
        random_facts = await self.db.facts.select_random(limit=5) or []

        # сборка контекста
        context["articles"] = processed_articles
        context["facts"] = [item["fact"] for item in random_facts]

        return context

    @handle_basic_db_errors
    async def articles(self) -> dict:
        """
        Информация для страницы статей
        """

        def enum_key_to_value(enum_class: type[Enum], key: str) -> str | None:
            """
            Преобразование ключа enum в его значение (value)
            """

            try:
                value = getattr(enum_class, key)
                return str(value)
            except ValueError:
                return None

        rows = await self.db.tags.count_tags()

        tags = {}
        for row in rows:
            tag_type = row["type"]
            tag_value = row["value"]

            if tag_type == "aircraft_type":
                tag_value = enum_key_to_value(AircraftTypes, tag_value)
            elif tag_type == "engine_type":
                tag_value = enum_key_to_value(EngineTypes, tag_value)
            elif tag_type == "status":
                tag_value = enum_key_to_value(AircraftStatus, tag_value)
            elif tag_type == "aircraft_purpose":
                tag_value = enum_key_to_value(AircraftPurpose, tag_value)

            if tag_value is None:
                continue

            if tag_type not in tags:
                tags[tag_type] = []
            tags[tag_type].append(tag_value)

        context = {"tags": tags}

        return context
