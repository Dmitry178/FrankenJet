""" Обработчики команд """

from aiogram import types, Router
from aiogram.filters import Command

from app.core.logs import bot_logger

handlers_router = Router()


@handlers_router.message(Command("id"))
async def id_handler(message: types.Message):
    """
    Обработчик команды /id
    """

    user_id = message.from_user.id
    msg = f"Ваш ID: <b>{user_id}</b>"

    try:
        await message.answer(msg)

    except Exception as ex:
        bot_logger.exception(ex)
