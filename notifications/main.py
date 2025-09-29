import asyncio

from app.bot import dp, bot
from app.bot.events import start_bot, stop_bot
from app.bot.handlers import handlers_router
from app.broker.subscribers import broker
from app.core.logs import bot_logger


async def main() -> None:
    async with broker:
        # запуск брокера
        await broker.start()
        bot_logger.info("Брокер RabbitMQ запущен")

        # удаление webhooks, если есть
        await bot.delete_webhook()

        # регистрация роутеров
        dp.include_router(handlers_router)

        # регистрация событий
        dp.startup.register(start_bot)
        dp.shutdown.register(stop_bot)

        # запуск бота
        bot_logger.info("Запуск бота")
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        bot_logger.info("Бот остановлен")
