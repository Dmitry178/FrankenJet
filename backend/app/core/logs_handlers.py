import asyncio
import logging
import traceback

from asyncio import AbstractEventLoop

from app.config.env import settings
from app.schemas.logs import SLogEntry
from app.services.bot import BotServices


class NotificationHandler(logging.Handler):
    """
    Перехватчик логов для отправки ошибок в бот уведомлений
    """

    def __init__(self, loop: AbstractEventLoop, bot: BotServices) -> None:
        super().__init__()
        self.loop = loop
        self.bot = bot

    def emit(self, record):
        # проверка уровня лога
        if record.levelno >= logging.ERROR:  # TODO сделать настройку минимального уровня отправки логов
            formatter = logging.Formatter()  # получаем время
            log_entry = SLogEntry(
                level=record.levelname,
                message=record.getMessage(),
                module=record.module,
                funcName=record.funcName,
                lineno=record.lineno,
                asctime=formatter.formatTime(record),
                exc_text=record.exc_text,
                stack_info=record.stack_info,
            )

            # сохраняем traceback, если есть
            if record.exc_info:
                log_entry.traceback = "".join(
                    traceback.format_exception(record.exc_info[1])
                    # traceback.format_exception(*record.exc_info)
                )

            # отправка ошибки в бот уведомлений
            asyncio.run_coroutine_threadsafe(self.send_log(log_entry), self.loop)

    async def send_log(self, log_entry: SLogEntry) -> None:
        await self.bot.send_logs(log_entry)


async def add_logging_handler(logger: logging.Logger, bot: BotServices):
    """
    Добавление хэндлера к логгеру
    """

    if not settings.RMQ_CONN:
        return

    loop = asyncio.get_running_loop()
    handler = NotificationHandler(loop=loop, bot=bot)
    logger.addHandler(handler)
