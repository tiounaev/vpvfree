# bot/main.py
import logging
import asyncio

from aiogram import Bot, Dispatcher
from bot.config import settings
from bot.scheduler import scheduler
from bot.services.db import engine, Base

from bot.handlers.core import register_handlers as register_core
from bot.handlers.trial import register_handlers as register_trial
from bot.handlers.purchase import register_handlers as register_purchase
from bot.handlers.admin import router as admin_router  # Используем router напрямую
from bot.handlers.referral import register_handlers as register_referral

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    logger.info("🚀 Bot is starting…")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    scheduler.start()


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    logger.info("🔻 Bot is shutting down…")
    scheduler.shutdown()
    await bot.session.close()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Регистрация всех хендлеров
    dp.include_router(admin_router)
    register_core(dp)
    register_trial(dp)
    register_purchase(dp)
    register_referral(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
