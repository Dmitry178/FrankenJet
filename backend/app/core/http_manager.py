""" AIOHTTP менеджер сессий """

import aiohttp
import asyncio

from aiohttp import ClientSession, ClientError, ClientResponseError, TCPConnector, ClientResponse
from fastapi import HTTPException

from app.core.logs import logger


class HTTPManager:
    def __init__(self, max_retries: int = 3):
        self.session: ClientSession | None = None
        self._lock = asyncio.Lock()
        self.max_retries = max_retries

    async def get_session(self) -> ClientSession:
        async with self._lock:
            if self.session is None or self.session.closed:
                await self._create_session()
            return self.session

    async def _create_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

        self.session = ClientSession(
            connector=TCPConnector(limit=100, limit_per_host=20),
            timeout=aiohttp.ClientTimeout(total=30)
        )

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """
        Запрос с повторными попытками
        """

        session = await self.get_session()

        for attempt in range(self.max_retries):
            try:
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return response

            except (ClientError, ClientResponseError) as ex:
                if attempt == self.max_retries - 1:
                    logger.error(f"Не совершить запрос после {self.max_retries} попыток")
                    logger.exception(ex)
                    raise HTTPException(
                        status_code=500,
                        detail=f"Request failed after {self.max_retries} attempts: {str(ex)}"
                    )
                await asyncio.sleep(1 * (attempt + 1))
