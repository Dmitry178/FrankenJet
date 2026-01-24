""" События телеграм-бота """

import json

from aiogram.types import CallbackQuery

from app.bot import bot, dp
from app.broker.subscribers import broker
from app.core.config import bot_settings, RMQ_FJ_INPUT_QUEUE
from app.core.logs import bot_logger


async def start_bot() -> None:
    """
    Сообщение администраторам о запуске бота
    """

    text = f"<b>{bot_settings.APP_NAME}</b>. Бот запущен 🟢"
    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=text)
    return None


async def stop_bot() -> None:
    """
    Сообщение администраторам об остановке бота
    """

    text = f"<b>{bot_settings.APP_NAME}</b>. Бот остановлен 🔴"
    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=text)
    return None


async def send_response_and_update_message(message: dict, callback_query: CallbackQuery) -> None:
    """
    Отправка сообщения в RabbitMQ и удаление кнопок
    """

    try:
        await broker.publish(json.dumps(message), queue=RMQ_FJ_INPUT_QUEUE)
        bot_logger.info("Решение по модерации отправлено в RabbitMQ")

    except Exception as ex:
        bot_logger.exception("Ошибка отправки сообщения", extra={"error": str(ex)})
        await bot.answer_callback_query(callback_query.id, text="Ошибка отправки ответа")
        return

    # удаление кнопок после отправки сообщения
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None,
    )
    await bot.answer_callback_query(callback_query.id, text="Ответ отправлен")
    return None


@dp.callback_query()
async def handle_callback(callback_query: CallbackQuery):
    callback_data = callback_query.data
    parts = callback_data.split(":")
    action = parts[0]

    if action == "admin_auth":
        # отправка решения по аутентификации админа в бэкенде
        user_id = parts[1]
        user = parts[2]
        result = parts[3]
        message = {
            "type": "admin_auth_response",
            "id": user_id,
            "user": user,
            "result": result
        }
        await send_response_and_update_message(message, callback_query)

    elif action == "moderation":
        # отправка решения о модерации в бэкенд
        comment_id = parts[1]
        decision = parts[2]
        message = {
            "type": "moderation_response",
            "comment_id": comment_id,
            "decision": decision
        }
        await send_response_and_update_message(message, callback_query)
