import asyncio

from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError, ConflictError

from app.core.logs import logger


class ESManager:

    def __init__(self, url: Optional[str] = None, max_retries: int = 3):
        self.url = url
        self.max_retries = max_retries
        self.es: Optional[AsyncElasticsearch] = AsyncElasticsearch([url]) if url else None

    async def start(self):
        """
        Запуск менеджера
        """

        if self.url:
            try:
                # проверка, доступен ли ES
                await self.es.ping()
                logger.info("Elasticsearch подключен")

            except Exception as e:
                logger.error(f"Elasticsearch недоступен: {e}")
                self.es = None  # отключаем, если не доступен

    async def close(self):
        if self.es:
            await self.es.close()

    @asynccontextmanager
    async def context(self):
        try:
            await self.start()
            yield self
        finally:
            await self.close()

    async def search(self, query: Dict[str, Any], index="articles") -> Optional[Dict[str, Any]]:
        """
        Поиск
        """

        if not self.es:
            return None

        for attempt in range(self.max_retries):
            try:
                result = await self.es.search(index=index, body=query)
                return result

            except ConnectionError:
                if attempt == self.max_retries - 1:
                    logger.error(f"ES недоступен после {self.max_retries} попыток")
                    return None
                logger.warning(f"Ошибка подключения к ES (попытка {attempt + 1})")
                await asyncio.sleep(1 * (attempt + 1))

            except Exception as e:
                logger.error(f"Ошибка при поиске в ES: {e}")
                return None

    async def index_document(self, index: str, doc_id: str, document: Dict[str, Any]) -> bool:
        """
        Индексирование документа
        """

        if not self.es:
            return False

        for attempt in range(self.max_retries):
            try:
                await self.es.index(index=index, id=doc_id, document=document)
                return True

            except ConnectionError:
                if attempt == self.max_retries - 1:
                    logger.error(f"ES недоступен для индексации после {self.max_retries} попыток")
                    return False
                logger.warning(f"Ошибка подключения к ES при индексации (попытка {attempt + 1})")
                await asyncio.sleep(1 * (attempt + 1))

            except Exception as e:
                logger.error(f"Ошибка при индексации в ES: {e}")
                return False

    async def delete_document(self, index: str, doc_id: str) -> bool:
        """
        Удаление документа
        """

        if not self.es:
            return False

        for attempt in range(self.max_retries):
            try:
                await self.es.delete(index=index, id=doc_id)
                return True

            except NotFoundError:
                logger.warning(f"Документ {doc_id} не найден в индексе {index}")
                return False

            except ConnectionError:
                if attempt == self.max_retries - 1:
                    logger.error(f"ES недоступен для удаления после {self.max_retries} попыток")
                    return False
                logger.warning(f"Ошибка подключения к ES при удалении (попытка {attempt + 1})")
                await asyncio.sleep(1 * (attempt + 1))

            except Exception as e:
                logger.error(f"Ошибка при удалении из ES: {e}")
                return False
