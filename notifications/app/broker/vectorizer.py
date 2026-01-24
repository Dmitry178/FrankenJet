""" Обработка сообщений от Vectorizer """

from dataclasses import dataclass

from app.bot.utils import send_logs_to_bot, send_notification_to_bot, send_message_to_admin, prepare_expandable
from app.broker.utils import extract_broker_message
from app.core.logs import bot_logger

SERVICE_NAME = "Vectorizer"


@dataclass
class VMsgTypes:
    """
    Типы сообщений на отправку в бот
    """

    log = "log"
    info = "info"


async def proceed_messages_from_vectorizer(message: str) -> None:
    """
    Обработка сообщений от Vectorizer
    """

    try:
        msg_type, msg_data = extract_broker_message(message)

        match msg_type:

            # отправка логов в бот
            case VMsgTypes.log:
                await send_logs_to_bot(msg_data, SERVICE_NAME)

            # отправка технического уведомления в бот
            case VMsgTypes.info:
                await send_notification_to_bot(msg_data)

            case _:
                msg = f'Ошибка типа сообщения "{msg_type}"'
                bot_logger.error(msg)
                await send_message_to_admin(f"⚠️ {msg}\n{message}")

    except (Exception, ValueError) as ex:
        msg = "Ошибка обработки сообщения из RabbitMQ"
        bot_logger.exception(msg, extra={"error": str(ex)})
        err_msg = prepare_expandable(f"⚠️ {msg}", str(ex))
        await send_message_to_admin(err_msg)

    return None
