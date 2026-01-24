from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_auth_keyboard(id_: str, user: str):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="OK ✅",
        callback_data=f"admin_auth:{id_}:{user}:ok")
    )
    builder.add(types.InlineKeyboardButton(
        text="Logout ❌",
        callback_data=f"admin_auth:{id_}:{user}:logout")
    )
    builder.add(types.InlineKeyboardButton(
        text="Block 🚫",
        callback_data=f"admin_auth:{id_}:{user}:block")
    )
    return builder.as_markup()


def get_moderation_keyboard(comment_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Одобрить 👍",
        callback_data=f"moderation:{comment_id}:approve")
    )
    builder.add(types.InlineKeyboardButton(
        text="Отклонить 👎",
        callback_data=f"moderation:{comment_id}:reject")
    )
    return builder.as_markup()
