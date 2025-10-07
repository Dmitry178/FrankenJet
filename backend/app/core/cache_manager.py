""" Менеджер FastApiCache """

import redis.asyncio as redis

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from functools import wraps
from typing import Callable, Awaitable


class CacheManager:
    def __init__(self, url: str | None = None, password: str | None = None):
        self.password = password
        self.url = url
        self._backend = None
        self._redis_client = None

    async def start(self):
        if self.url:
            self._redis_client = redis.from_url(self.url, password=self.password)
            self._backend = RedisBackend(self._redis_client)
            FastAPICache.init(self._backend, prefix="cache")

    async def close(self):
        if self._redis_client:
            await self._redis_client.aclose()

    def cached(self, *, ttl: int = 300, namespace: str = ""):
        """
        Декоратор для кэширования функций
        """

        if not self.url:
            # если Redis не настроен — возвращаем оригинальную функцию
            def null_cached(func: Callable[..., Awaitable]):
                @wraps(func)
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)
                return wrapper
            return null_cached

        # если Redis настроен — используем оригинальный декоратор fastapi-cache2
        def actual_cached(func: Callable[..., Awaitable]):
            return cache(namespace=namespace, expire=ttl)(func)

        return actual_cached
