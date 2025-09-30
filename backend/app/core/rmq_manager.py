import asyncio

from aiormq import AMQPConnectionError, ChannelClosed, AMQPError
from contextlib import asynccontextmanager
from faststream.rabbit import RabbitBroker

from app.core.logs import logger


class RMQManager:
    def __init__(self, url: str | None = None, max_retries: int = 3):

        self.url = url
        self.max_retries = max_retries
        self.broker = RabbitBroker(url) if url else None

    async def start(self):
        if self.url:
            await self.broker.connect()

    async def close(self):
        if self.url:
            await self.broker.stop()

    @asynccontextmanager
    async def context(self):
        try:
            await self.start()
            yield self
        finally:
            await self.close()

    async def publish(self, message: str, queue: str):
        """
        Публикация сообщения с повторными попытками
        """

        if not self.url:
            return

        for attempt in range(self.max_retries):
            try:
                await self.broker.publish(message, queue=queue)
                return

            except (AMQPConnectionError, ChannelClosed, AMQPError) as ex:
                if attempt == self.max_retries - 1:
                    logger.error(f"Не удалось опубликовать сообщение после {self.max_retries} попыток")
                    raise RuntimeError(f"Ошибка публикации сообщения после {self.max_retries} попыток")

                logger.warning(f"Ошибка публикации (попытка {attempt + 1}): {ex}")

                # экспоненциальная задержка перед повторной попыткой отправки сообщения
                await asyncio.sleep(1 * (attempt + 1))

                # повторное подключение
                try:
                    await self.broker.stop()
                except Exception:  # noqa
                    pass

                await self.broker.connect()

    def subscriber(self, queue: str):
        """
        Декоратор для подписки на очередь
        """

        if not self.url:
            # если RMQ не настроен — возвращаем оригинальную функцию
            def null_subscriber(func):
                return func
            return null_subscriber

        return self.broker.subscriber(queue)

    async def run_consumers(self):
        """
        Запуск брокера с подписчиками
        """

        if not self.url:
            return

        # noinspection PyUnresolvedReferences
        await self.broker.run()
