import json

from dataclasses import dataclass

from app.bot import bot
from app.bot.keyboards import get_admin_auth_keyboard, get_moderation_keyboard
from app.bot.utils import prepare_expandable
from app.core.config import bot_settings
from app.core.logs import bot_logger


@dataclass
class MsgTypes:
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
        json_data = json.loads(message)
        msg_type = json_data.get("type")
        msg_data = json_data.get("data")

        if not msg_data:
            raise ValueError

        match msg_type:

            case MsgTypes.log:
                message_text = (
                    f'⚠️ <b>Log Level:</b> {msg_data.get("level")}\n'
                    f'📝 <b>Message:</b> {msg_data.get("message")}\n'
                    f'📦 <b>Module:</b> {msg_data.get("module")}\n'
                    f'🔧 <b>Function:</b> {msg_data.get("funcName")}\n'
                    f'📄 <b>File:</b> {msg_data.get("module")}.py (line {msg_data.get("lineno")})\n'
                    f'🕒 <b>Time:</b> {msg_data.get("asctime")}\n'
                )

                if msg_data.get("exc_text"):
                    message_text += f'\n❌ <b>Exception:</b>\n<code>{msg_data.get("exc_text")}</code>\n'

                if msg_data.get("stack_info"):
                    message_text += f'\n🔍 <b>Stack Info:</b>\n<code>{msg_data.get("stack_info")}</code>\n'

                disable_notification = msg_data.get("level") in {"DEBUG", "INFO", "WARNING"}

                await bot.send_message(
                    chat_id=bot_settings.TELEGRAM_ADMIN_ID,
                    text=message_text,
                    disable_notification=disable_notification
                )

                if msg_data.get("traceback"):
                    expandable_traceback = prepare_expandable(None, msg_data.get("traceback"))
                    await bot.send_message(
                        chat_id=bot_settings.TELEGRAM_ADMIN_ID,
                        text=expandable_traceback,
                        parse_mode="MarkdownV2"
                    )

            case MsgTypes.info:
                # отправка технического уведомления в бот
                message_text = f'<b>{msg_data.get("caption")}:</b> {msg_data.get("message")}'
                await bot.send_message(
                    chat_id=bot_settings.TELEGRAM_ADMIN_ID,
                    text=message_text,
                    disable_notification=True
                )

            case MsgTypes.notification:
                # отправка уведомления в бот
                await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=msg_data)

            case MsgTypes.auth_notification:
                # сообщение об аутентификации администратора
                message_text = (
                    "❗️<b>Произведён вход в приложение</b>\n"
                    f'<b>Пользователь:</b> {msg_data.get("email")} (id: {msg_data.get("user-id")})\n'
                    f'<b>IP:</b> {msg_data["client-ip"]}\n'
                    f'<b>User Agent:</b> {msg_data["user-agent"]}'
                )

                keyboard = get_admin_auth_keyboard(msg_data.get("user-id"))
                await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=message_text, reply_markup=keyboard)

            case MsgTypes.moderation:
                # модерация комментария
                expandable_comment = prepare_expandable("Модерация комментария", msg_data.get("comment"))
                keyboard = get_moderation_keyboard(msg_data.get("id"))
                await bot.send_message(
                    chat_id=bot_settings.TELEGRAM_ADMIN_ID,
                    text=expandable_comment,
                    reply_markup=keyboard,
                    parse_mode="MarkdownV2"
                )

            case _:
                bot_logger.error(f'Ошибка типа сообщения "{msg_type}"')

    except (Exception, ValueError) as ex:
        message = "Ошибка обработки сообщения из RabbitMQ"
        bot_logger.exception(f"{message}: {ex}")
        await bot.send_message(f"⚠️ {message}")
