from dataclasses import dataclass

from app.bot import bot
from app.bot.keyboards import get_admin_auth_keyboard, get_moderation_keyboard
from app.bot.utils import prepare_expandable, send_logs_to_bot, send_notification_to_bot, send_message_to_admin
from app.broker.utils import extract_broker_message
from app.core.config import bot_settings
from app.core.logs import bot_logger

SERVICE_NAME = "Frankenjet"


@dataclass
class FJMsgTypes:
    """
    Типы сообщений на отправку в бот
    """

    log = "log"
    info = "info"
    notification = "notification"
    auth_notification = "auth_notification"
    moderation = "moderation"


async def proceed_messages_from_frankenjet(message: str) -> None:
    """
    Обработка сообщений от FrankenJet
    """

    try:
        msg_type, msg_data = extract_broker_message(message)

        match msg_type:

            # отправка логов в бот
            case FJMsgTypes.log:
                await send_logs_to_bot(msg_data, SERVICE_NAME)

            # отправка технического уведомления в бот
            case FJMsgTypes.info:
                await send_notification_to_bot(msg_data)

            # отправка уведомления в бот
            case FJMsgTypes.notification:
                await send_notification_to_bot(msg_data)

            # сообщение об аутентификации администратора
            case FJMsgTypes.auth_notification:
                user_id = msg_data.get("id")
                user = msg_data.get("user", "")
                message_text = (
                    "❗️<b>Произведён вход в приложение</b>\n"
                    f'<b>Пользователь:</b> {user}\n'
                    f'<b>IP:</b> {msg_data.get("client-ip", "")}\n'
                    f'<b>User Agent:</b> {msg_data.get("user-agent", "")}'
                )
                keyboard = get_admin_auth_keyboard(user_id, user)
                await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=message_text, reply_markup=keyboard)

            # модерация комментария
            case FJMsgTypes.moderation:
                expandable_comment = prepare_expandable("Модерация комментария", msg_data.get("comment"))
                keyboard = get_moderation_keyboard(msg_data.get("id"))
                await bot.send_message(
                    chat_id=bot_settings.TELEGRAM_ADMIN_ID,
                    text=expandable_comment,
                    reply_markup=keyboard,
                    parse_mode="MarkdownV2"
                )

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
