"""
Индексирование статей в ElasticSearch
"""

import asyncio
import json
import logging
import os
import re
import sys

from app.core import ESManager

sys.path.append("/code")

from environs import Env
from pathlib import Path

from app.db.models import Countries, Articles, Aircraft
from scripts.init_data import DataUtils

# путь к статьям
BASE_ARTICLES_PATH = "./scripts/articles"

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
                }
            },
            "analyzer": {
                "my_synonym_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "icu_normalizer",
                        "lowercase",
                        "city_synonyms",
                        "russian_morphology",
                        "english_morphology",
                        "snowball"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "my_synonym_analyzer"},
            "content": {"type": "text", "analyzer": "my_synonym_analyzer"},
            "tags": {"type": "keyword"},
            "entities": {"type": "keyword"}
        }
    }
}


class InitData:

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Нормализация данных перед отправкой в elasticsearch на индексацию
        """

        normalized = text.lower().replace("ё", "е")

        # удаление всех символов, кроме букв, цифр и пробелов
        normalized = re.sub(r"[^\w\s]", " ", normalized)

        # замена множественных пробелов на один и удаление ведущих/концевых пробелов
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    async def gen_es_data(self, articles_data: list, aircraft_data: list, countries_data: list, normalize=True) -> list:
        """
        Подготовка данных к индексации elasticsearch
        """

        # преобразование aircraft_data и countries_data в словарь для более удобной обработки
        aircraft = {item["article_id"]: {k: v for k, v in item.items() if k != "article_id"} for item in aircraft_data}
        countries = {item["id"]: item["name"] for item in countries_data}

        es_docs = []  # итоговый документ для индексации

        for item in articles_data:
            article_id = item["id"]
            content = self.normalize_text(item["content"]) if normalize else item["content"]

            if not aircraft_data:
                title = item["title"]
                tags = [item["article_category"]]
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

            if normalize:
                title = self.normalize_text(title)
                tags = [self.normalize_text(tag) for tag in tags]  # нормализация тегов

            idx = re.sub(r'^_|(\.[^.]*)$', '', item["filename"])

            # сборка итогового документа
            doc = {
                "_index": idx,
                "_id": str(article_id),
                "_source": {
                    "title": title,
                    "content": content,
                    "tags": tags,
                    # "entities"
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


async def main() -> None:

    env = Env()
    env.read_env()

    es_url = env.str("ELASTICSEARCH_URL")
    if not es_url:
        logger.warning("Строка подключения к Elasticsearch отсутствует")
        sys.exit(0)

    es_manager = ESManager(url=es_url)

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

    # индексация статей
    await es_manager.start()

    try:
        # Проход по каждому документу из подготовленного списка
        for doc in es_doc:
            index_name = doc["_index"]
            doc_id = doc["_id"]
            source_data = doc["_source"]

            # проверка существования индекса перед индексацией документа
            try:
                index_exists = await es_manager.es.indices.exists(index=index_name)

            except Exception as ex:
                logger.error(f"Ошибка при проверке существования индекса {index_name}: {ex}")
                continue

            if not index_exists:
                try:
                    # создание индекса с настройками
                    await es_manager.es.indices.create(index=index_name, body=index_settings)
                    logger.info(f'Индекс "{index_name}" создан')

                except Exception as ex:
                    logger.error(f"Ошибка при создании индекса {index_name}: {ex}")
                    continue

            # индексация документа через ESManager
            success = await es_manager.index_document(index=index_name, doc_id=doc_id, document=source_data)

            if success:
                logger.info(f'Документ ID {doc_id} успешно проиндексирован в индекс "{index_name}"')
            else:
                logger.info(f'Ошибка индексации документа ID {doc_id} в индекс "{index_name}"')

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
