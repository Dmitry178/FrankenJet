""" Настройка логирования """

import logging
import sys
import traceback

from app.config.env import settings


class NotificationHandler(logging.Handler):
    """
    Перехватчик логов для отправки ошибок в бот уведомлений
    """

    def emit(self, record):
        # проверка уровня лога
        if record.levelno >= logging.ERROR:
            formatter = logging.Formatter()  # получаем время
            log_entry = {
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "funcName": record.funcName,
                "lineno": record.lineno,
                "asctime": formatter.formatTime(record),
                "exc_text": record.exc_text,
                "stack_info": record.stack_info,
            }

            # сохраняем traceback, если есть
            if record.exc_info:
                log_entry['traceback'] = ''.join(
                    traceback.format_exception(record.exc_info[1])
                )

            # отправка ошибки в бот уведомлений
            # send_to_bot(log_entry)

        # вывод сообщения как обычно
        sys.stdout.write(self.format(record) + '\n')


# обработчики
handlers = [
    logging.StreamHandler(sys.stdout)
]
# if settings.RMQ_CONN:
#     handlers.append(NotificationHandler())

# конфиг логов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers,
)

logger = logging.getLogger(settings.APP_NAME)
