import asyncio

from contextlib import asynccontextmanager
from typing import Dict, Any

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError, AuthenticationException

from app.config.env import settings, AppMode
from app.core.logs import logger


class ESManager:

    def __init__(
            self,
            url: str | None = None,
            password: str | None = None,
            max_retries: int = 3,
            use_ssl: bool = None
    ):
        self.url = url
        self.password = password
        self.max_retries = max_retries
        self.use_ssl = use_ssl if use_ssl is not None else (settings.APP_MODE == AppMode.production)
        self.es: AsyncElasticsearch | None = None

    async def start(self):
        """
        Запуск менеджера
        """

        if not self.url:
            return

        try:

            headers = {
                "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8",
                "Accept": "application/vnd.elasticsearch+json; compatible-with=8"
            }

            basic_auth = ("elastic", self.password) if self.password else None

            self.es = AsyncElasticsearch(
                [self.url],
                headers=headers,
                basic_auth=basic_auth,
                verify_certs=self.use_ssl,
                ssl_show_warn=self.use_ssl
            )

            await self.es.ping()  # проверка доступности ES

        except (ConnectionError, AuthenticationException) as ex:
            logger.error(f"Ошибка подключения к Elasticsearch: {ex}")
            self.es = None

        except Exception as ex:
            logger.exception(f"Elasticsearch недоступен: {ex}")
            self.es = None

    async def close(self):
        if not self.es:
            return

        try:
            await self.es.close()

        except Exception as ex:
            logger.exception(f"Ошибка закрытия Elasticsearch: {ex}")

        finally:
            self.es = None

    @asynccontextmanager
    async def context(self):
        try:
            await self.start()
            yield self
        finally:
            await self.close()

    async def search(self, query: Dict[str, Any], index: str | list = "articles") -> Dict[str, Any] | None:
        """
        Индексированный поиск
        """

        if not self.es:
            return None

        for attempt in range(self.max_retries):
            try:
                return await self.es.search(index=index, body=query)

            except ConnectionError:
                if attempt == self.max_retries - 1:
                    logger.error(f"ES недоступен после {self.max_retries} попыток")
                    return None
                logger.warning(f"Ошибка подключения к ES (попытка {attempt + 1})")
                await asyncio.sleep(1 * (attempt + 1))

            except Exception as ex:
                logger.error(f"Ошибка при поиске в ES: {ex}")
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

            except Exception as ex:
                logger.error(f"Ошибка при индексации в ES: {ex}")
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

            except Exception as ex:
                logger.error(f"Ошибка при удалении из ES: {ex}")
                return False

    async def health_check(self) -> bool:
        """
        Проверка подключения Elasticsearch
        """

        if not self.es:
            return False

        try:
            return await self.es.ping()

        except Exception as ex:
            logger.exception(f"Ошибка проверки Elasticsearch: {ex}")
            return False
