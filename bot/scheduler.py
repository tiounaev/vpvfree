import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from bot.config import settings
from bot.generator import CONFIG_PATH, load_config, save_config

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

bot = Bot(token=settings.BOT_TOKEN)


async def async_remove_user_and_notify(user_id: int, uuid: str):
    conf = load_config()
    found = False

    for inbound in conf.get("inbounds", []):
        if "users" in inbound:
            before = len(inbound["users"])
            inbound["users"] = [
                u for u in inbound["users"]
                if u.get("uuid") != uuid and u.get("password") != uuid
            ]
            if len(inbound["users"]) < before:
                found = True

    if found:
        save_config(conf)
        logger.info(f"[scheduler] Пользователь с UUID {uuid} удалён")
        await bot.send_message(
            chat_id=user_id,
            text="⛔️ Ваш тестовый доступ истёк. Чтобы получить постоянный доступ перейдите в раздел *Купить VPN*"

        )


def remove_user_and_notify(user_id: int, uuid: str):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Нет активного event loop: создаём и запускаем вручную
        asyncio.run(async_remove_user_and_notify(user_id, uuid))
    else:
        # Есть активный loop — запускаем в фоне
        loop.create_task(async_remove_user_and_notify(user_id, uuid))
