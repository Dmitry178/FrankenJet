import html

from aiogram.types import LinkPreviewOptions

from app.bot import bot
from app.core.config import bot_settings


def prepare_message(text: str, esc_special: bool = True) -> str:
    """
    Подготовка текста для вывода в телеграм-боте (для Markdown V2)
    """

    if esc_special:
        # полное экранирование сообщения
        special_chars = r"_*[]()~`>#+-=|{}.!".replace("\\", "\\\\")
    else:
        # частичное экранирование сообщения (кроме символа * для выделения текста и > | для выпадающего списка)
        special_chars = r"_[]()~`#+-={}.!".replace("\\", "\\\\")

    escaped_str = ""

    for char in text:
        if char in special_chars:
            escaped_str += "\\" + char
        else:
            escaped_str += char

    return escaped_str


def escape_mdv2(text: str | None) -> str:
    """
    Экранирование специальных символов MarkdownV2
    """

    if not text:
        return ""

    md_chars = r"\_*[]()~`>#+-=|{}.!"

    for ch in md_chars:
        text = text.replace(ch, '\\' + ch)

    return text


def prepare_expandable(caption: str | None, text: str | None) -> str:
    """
    Подготовка текста для Expandable block (для Markdown V2)
    """

    if not text:
        return ""

    caption = escape_mdv2(caption) + "\n" if caption else ""

    lines = text.split("\n")
    modified_lines = [">" + escape_mdv2(line) for line in lines]
    modified_text = "\n".join(modified_lines)

    return f"\n**>{caption}{modified_text}||"


def prepare_log(msg_data: dict, service_name: str) -> str:
    """
    Подготовка текста лога для вывода в бот
    """

    message_text = (
        f'🧩 <b>Service:</b> {service_name}\n'
        f'⚠️ <b>Log Level:</b> {msg_data.get("level")}\n'
        f'📝 <b>Message:</b> {html.escape(msg_data.get("message"))}\n'
        f'📦 <b>Module:</b> {msg_data.get("module")}\n'
        f'🔧 <b>Function:</b> {msg_data.get("funcName")}\n'
        f'📄 <b>File:</b> {msg_data.get("module")}.py (line {msg_data.get("lineno")})\n'
        f'🕒 <b>Time:</b> {msg_data.get("asctime")}\n'
    )

    if msg_data.get("exc_text"):
        message_text += f'\n❌ <b>Exception:</b>\n<code>{html.escape(msg_data.get("exc_text"))}</code>\n'

    if msg_data.get("stack_info"):
        message_text += f'\n🔍 <b>Stack Info:</b>\n<code>{html.escape(msg_data.get("stack_info"))}</code>\n'

    return message_text


async def send_logs_to_bot(msg_data: dict, service_name: str):
    """
    Отправка логов в бот
    """

    message_text = prepare_log(msg_data, service_name)
    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=message_text)

    if msg_data.get("traceback"):
        expandable_traceback = prepare_expandable(None, msg_data.get("traceback"))
        await bot.send_message(
            chat_id=bot_settings.TELEGRAM_ADMIN_ID,
            text=expandable_traceback,
            parse_mode="MarkdownV2",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )


async def send_message_to_admin(text: str):
    """
    Отправка сообщения админу
    """

    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=text)


async def send_notification_to_bot(msg_data: dict | str):
    """
    Отправка уведомления в бот
    """

    if isinstance(msg_data, dict):
        caption = msg_data.get("caption")
        message = msg_data.get("message") or ""
        message_text = (f"<b>{caption}:</b> " if caption else "") + message
    else:
        message_text = str(msg_data or "")

    await send_message_to_admin(message_text)
