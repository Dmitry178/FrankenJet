"""
Индексирование статей в ElasticSearch
"""

import asyncio
import json
import logging
import os
import re
import sys

sys.path.append("/code")

from environs import Env
from pathlib import Path

from app.core import ESManager
from app.db.models import Countries, Articles, Aircraft
from scripts.init_data import DataUtils

# путь к статьям
BASE_ARTICLES_PATH = "./scripts/articles"

# название индекса
ARTICLES_INDEX = "articles"

index_settings = {
    "settings": {
        "analysis": {
            "filter": {
                "city_synonyms": {
                    "type": "synonym",
                    "synonyms": [
                        "санкт-петербург, петербург, питер, спб, с-пб, с-петербург, петроград, ленинград",
                        "москва, мос, мск",
                        "екатеринбург, екат, ебург, ёбург, екб, свердловск"
                    ]
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                }
            },
            "analyzer": {
                "custom_synonym_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "icu_normalizer",
                        "lowercase",
                        "city_synonyms",
                        "russian_stemmer",
                        "english_stemmer",
                        "snowball"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "custom_synonym_analyzer"},
            "content": {"type": "text", "analyzer": "custom_synonym_analyzer"},
            "tags": {"type": "keyword"},
            "image_url": {"type": "keyword"},
        }
    }
}


class InitData:

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Нормализация данных перед отправкой в elasticsearch на индексацию
        """

        if not text:
            return ""

        normalized = text.lower().replace("ё", "е")

        # удаление всех символов, кроме букв, цифр и пробелов
        normalized = re.sub(r"[^\w\s]", " ", normalized)

        # замена множественных пробелов на один и удаление ведущих/концевых пробелов
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Удаление основных MarkDown-символов
        """

        if not text:
            return ""

        # удаление символов "#" в начале строки
        cleaned = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)

        cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)  # **текст** → текст
        cleaned = re.sub(r"\*(.*?)\*", r"\1", cleaned)  # *текст* → текст
        cleaned = re.sub(r"__(.*?)__", r"\1", cleaned)  # __текст__ → текст
        cleaned = re.sub(r"_(.*?)_", r"\1", cleaned)  # _текст_ → текст

        # замена множественных пробелов на один и удаление пробелов в начале и конце строки
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned

    async def gen_es_data(
            self,
            articles_data: list,
            aircraft_data: list,
            countries_data: list,
            normalize=False
    ) -> list:
        """
        Подготовка данных к индексации elasticsearch
        """

        # преобразование aircraft_data и countries_data в словарь для более удобной обработки
        aircraft = {item["article_id"]: {k: v for k, v in item.items() if k != "article_id"} for item in aircraft_data}
        countries = {item["id"]: item["name"] for item in countries_data}

        es_docs = []  # итоговый документ для индексации

        for item in articles_data:
            article_id = item["id"]
            content = self.normalize_text(item["content"]) if normalize else self.clean_text(item["content"])
            slug = item["slug"]

            if not aircraft_data:
                title = item["title"]
                tags = [item["article_category"]]
                image_url = None
            else:
                aircraft_item = aircraft[article_id]
                title = aircraft_item["name"]
                if aircraft_item["name"] != aircraft_item["original_name"]:
                    title += " ({})".format(aircraft_item["original_name"])
                tags = [
                    item["article_category"],
                    aircraft_item["country_id"],
                    countries[aircraft_item["country_id"]],
                    aircraft_item["aircraft_type"],
                    aircraft_item["engine_type"],
                    aircraft_item["status"],
                ]
                image = str(aircraft_item["image_url"]).lstrip('_').replace("_", "-")
                image_url = f"/images/aircraft/{image}"

            if normalize:
                # нормализация тегов
                tags = [self.normalize_text(tag) for tag in tags if tag]
            else:
                # исключение None из тегов
                tags = [tag for tag in tags if tag]

            # сборка итогового документа
            doc = {
                "_id": str(article_id),
                "_source": {
                    "category": ARTICLES_INDEX,
                    "title": title,
                    "content": content,
                    "slug": slug,
                    "tags": tags,
                    "image_url": image_url,
                }
            }
            es_docs.append(doc)

        return es_docs


async def assemble_json(path: str, is_article=False) -> list[dict]:
    """
    Сборка json из файлов для добавления в БД
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
                # сохранение имени файла статьи
                content_filename = json_data.get("content")
                json_data["filename"] = content_filename

                # присоединение контента
                content_path = directory / content_filename
                with open(content_path, "r", encoding="utf-8") as content_file:
                    content_data = content_file.read()
                    json_data["content"] = content_data  # добавление контента

            result.append(json_data)

    return result


async def read_json(file: str) -> list:
    """
    Чтение json
    """

    file_path = Path(f"{os.getcwd()}/{file}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def index_articles(es_manager: ESManager):
    """
    Индексация статей
    """

    index_name = ARTICLES_INDEX

    # проверка существования индекса перед индексацией документа
    try:
        index_exists = await es_manager.es.indices.exists(index=index_name)
        if not index_exists:
            # создание индекса с настройками
            await es_manager.es.indices.create(index=index_name, body=index_settings)
            logger.info(f'Индекс "{index_name}" создан')

    except Exception as ex:
        logger.error(f"Ошибка при проверке/создании индекса {index_name}: {ex}")
        return

    # чтение и подготовка списка стран
    countries_data = await read_json("/scripts/data/countries.json")
    countries_data_model = DataUtils().convert_data_types(Countries, countries_data)

    # чтение и подготовка списка статей
    articles_data = await assemble_json(BASE_ARTICLES_PATH, is_article=True)
    articles_data_model = DataUtils().convert_data_types(Articles, articles_data)

    # чтение и подготовка списка воздушных судов
    aircraft_data = await assemble_json(f"{BASE_ARTICLES_PATH}/aircraft")
    aircraft_data_model = DataUtils().convert_data_types(Aircraft, aircraft_data)

    # подготовка статей к индексации
    es_doc = await InitData().gen_es_data(articles_data_model, aircraft_data_model, countries_data_model)

    try:
        # проход по каждому документу из подготовленного списка
        for doc in es_doc:
            doc_id = doc["_id"]
            source_data = doc["_source"]

            # индексация документа через ESManager
            success = await es_manager.index_document(index=index_name, doc_id=doc_id, document=source_data)

            if success:
                logger.info(f'Документ ID {doc_id} успешно проиндексирован в индекс "{index_name}"')
            else:
                logger.info(f'Ошибка индексации документа ID {doc_id} в индекс "{index_name}"')

    except Exception as ex:
        logger.exception(f"Ошибка индексации статей: {ex}")


async def main() -> None:
    env = Env()
    env.read_env()

    es_url = env.str("ELASTICSEARCH_URL")
    if not es_url:
        logger.warning("Строка подключения к Elasticsearch отсутствует")
        sys.exit(0)

    es_manager = ESManager(url=es_url)
    try:
        await es_manager.start()
        await index_articles(es_manager)
        # TODO: добавить индексацию фактов об авиации

    except Exception as ex:
        logger.exception(ex)

    finally:
        await es_manager.close()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger()

if __name__ == "__main__":
    asyncio.run(main())
