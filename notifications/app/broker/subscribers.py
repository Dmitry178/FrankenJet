""" Обработчики сообщений из RabbitMQ """

import json

from faststream.rabbit import RabbitBroker

from app.bot import bot
from app.bot.keyboards import get_admin_auth_keyboard, get_moderation_keyboard
from app.core.config import RMQ_NOTIFICATIONS_QUEUE, RMQ_ADMIN_AUTH_QUEUE, RMQ_MODERATION_QUEUE, bot_settings

broker = RabbitBroker(
    url=bot_settings.RMQ_CONN,
)


@broker.subscriber(RMQ_NOTIFICATIONS_QUEUE)
async def handle_notifications(data: str):
    """
    Отправка сообщений в бот
    """

    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=data)


@broker.subscriber(RMQ_ADMIN_AUTH_QUEUE)
async def handle_admin_auth(data: str):
    """
    Сообщение об аутентификации администратора
    """

    auth_info = json.loads(data)
    message_text = (
        f"❗️<b>Произведён вход в приложение</b>\n"
        f"<b>Пользователь:</b> {auth_info.get('email')} (id: {auth_info.get('user-id')})\n"
        f"<b>IP:</b> {auth_info['client-ip']}\n"
        f"<b>User Agent:</b> {auth_info['user-agent']}"
    )

    keyboard = get_admin_auth_keyboard(auth_info.get("user-id"))
    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=message_text, reply_markup=keyboard)


@broker.subscriber(RMQ_MODERATION_QUEUE)
async def handle_moderation_request(data: str):
    """
    Сообщение для модерации комментариев
    """

    moderation_data = json.loads(data)
    message_text = (
        f"<b>Модерация комментария:</b>\n"
        f"<b>Текст:</b>\n{moderation_data.get('comment')}"
    )
    # TODO: сделать expandable-сообщение

    keyboard = get_moderation_keyboard(moderation_data.get("id"))
    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=message_text, reply_markup=keyboard)
