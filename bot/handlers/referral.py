from aiogram import types, Dispatcher
from aiogram.filters import Command

async def referral_handler(message: types.Message):
    await message.reply("Your referral stats (заглушка)")

def register_handlers(dp: Dispatcher):
    dp.message.register(referral_handler, Command("referral"))
