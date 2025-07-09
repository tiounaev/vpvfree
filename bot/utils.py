# bot/utils.py

import functools
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.config import settings

def build_reply_menu() -> ReplyKeyboardMarkup:
    """
    Постоянное меню внизу чата:
      ℹ️ О проекте
      ⏳ Тестовый период | 🛒 Купить VPN
      👥 Рефералы      | 💬 Помощь и связь
      📜 Правила использования
    """
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ О проекте")],
            [KeyboardButton(text="⏳ Тестовый период"), KeyboardButton(text="🛒 Купить VPN")],
            [KeyboardButton(text="👥 Рефералы"),         KeyboardButton(text="💬 Помощь и связь")],
            [KeyboardButton(text="📜 Правила использования")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return kb

def admin_only(handler):
    @functools.wraps(handler)
    async def wrapper(message, *args, **kwargs):
        if message.from_user.id not in settings.ADMIN_IDS:
            return await message.reply("Access denied.")
        return await handler(message, *args, **kwargs)
    return wrapper
