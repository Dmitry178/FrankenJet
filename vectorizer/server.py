import asyncio

from asyncio import CancelledError

from app.bot import bot_services
from app.logs_handlers import add_logging_handler
from app.rmq_manager import app_rmq_manager
from app.service import serve
from app.logs import app_logger


async def main():
    app_logger.info(f"Starting gRPC service")
    try:
        if app_rmq_manager.url:
            await app_rmq_manager.start()
            bot_services.rmq = app_rmq_manager
            await add_logging_handler(app_logger, bot_services)
            app_logger.info("RabbitMQ connected")

        await bot_services.send_info("Сервис запущен 🟢")
        await serve()

    except (KeyboardInterrupt, CancelledError):
        app_logger.info("Stopping gRPC service")

    finally:
        await bot_services.send_info("Сервис остановлен 🔴")
        if app_rmq_manager.url:
            await app_rmq_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
