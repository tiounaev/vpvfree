# bot/handlers/core.py

from aiogram import types, Dispatcher
from aiogram.filters import Command
from bot.utils import build_reply_menu

async def start_handler(message: types.Message):
    await message.answer(
        "Добро пожаловать!\nВыберите пункт меню ниже:",
        reply_markup=build_reply_menu()
    )

def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
