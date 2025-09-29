""" События телеграм-бота """

from aiogram.types import CallbackQuery

from app.bot import bot, dp
from app.broker.subscribers import publish_to_backend
from app.core.config import bot_settings


async def start_bot():
    """
    Сообщение администраторам о запуске бота
    """

    text = f"<b>{bot_settings.APP_NAME}</b>. Бот запущен [{bot_settings.BUILD}]"
    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=text)


async def stop_bot():
    """
    Сообщение администраторам об остановке бота
    """

    text = f"<b>{bot_settings.APP_NAME}</b>. Бот остановлен [{bot_settings.BUILD}]"
    await bot.send_message(chat_id=bot_settings.TELEGRAM_ADMIN_ID, text=text)


@dp.callback_query()
async def handle_callback(callback_query: CallbackQuery):
    callback_data = callback_query.data
    parts = callback_data.split(":")
    action = parts[0]

    if action == "admin_auth":
        user_id = parts[1]
        result = parts[2]

        # отправка результата аутентификации в бэкенд
        publish_to_backend({
            "type": "admin_auth_response",
            "id": user_id,
            "result": result
        })

        # удаление кнопок после обработки
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=None,
        )
        await bot.answer_callback_query(callback_query.id, text=f"Отправлен ответ: {result}")

    elif action == "moderation":
        comment_id = parts[1]
        decision = parts[2]

        # отправка решения о модерации в бэкенд
        publish_to_backend({
            "type": "moderation_response",
            "comment_id": comment_id,
            "decision": decision
        })
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
        await bot.answer_callback_query(callback_query.id, text=f"Отправлен ответ: {decision}")
