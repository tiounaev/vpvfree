import asyncio
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from aiogram import types, Dispatcher
from aiogram.filters import Text
from sqlalchemy import select

from bot.config import settings
from bot.models import User, Trial
from bot.services.db import async_session
from bot.services.singbox import add_user
from bot.scheduler import scheduler, remove_user_and_notify


async def trial_handler(message: types.Message):
    tg_id = message.from_user.id

    async with async_session() as session:
        # Получаем пользователя
        result = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = result.scalar_one_or_none()

        # Если пользователя нет — создаём
        if user is None:
            user = User(
                telegram_id=tg_id,
                referral_code=uuid4().hex[:8]
            )
            session.add(user)
            await session.flush()

        # Проверяем наличие активного триала
        result2 = await session.execute(select(Trial).where(Trial.user_id == user.id))
        existing_trial = result2.scalar_one_or_none()

        if existing_trial:
            # Если триал уже истёк — сообщаем об этом
            if existing_trial.expires_at < datetime.now(timezone.utc):
                await message.answer(
                    "⛔️ Ваш тестовый доступ истёк. "
                    "Чтобы получить постоянный доступ перейдите в раздел *Купить VPN*.",
                    parse_mode="Markdown"
                )
                return

            # Иначе — напомним действующий ключ
            link = (
                f"vless://{existing_trial.uuid}@{settings.SINGBOX_HOST}:{settings.SINGBOX_PORT}"
                f"?security=none&encryption=none&type=tcp#ТестовыйПериод"
            )
            await message.answer(
                "🚀 Вы уже активировали тестовый период!\n\n"
                f"• Ваш ключ: `{link}`\n"
                f"• Действует до: {existing_trial.expires_at}",
                parse_mode="Markdown"
            )
            return

        # Генерируем новый триал
        new_uuid = str(uuid4())
        expires = datetime.now(timezone.utc) + timedelta(minutes=settings.TRIAL_DURATION_MINUTES)

        trial = Trial(user_id=user.id, uuid=new_uuid, expires_at=expires)
        session.add(trial)
        await session.commit()

    # Добавляем пользователя в конфиг
    await asyncio.get_event_loop().run_in_executor(None, add_user, {"uuid": new_uuid})

    # Планируем удаление и уведомление
    scheduler.add_job(
        func=remove_user_and_notify,
        trigger='date',
        run_date=expires,
        args=[tg_id, new_uuid],
        id=f"remove_{new_uuid}",
        misfire_grace_time=60
    )

    # Отправляем пользователю ссылку
    link = (
        f"vless://{new_uuid}@{settings.SINGBOX_HOST}:{settings.SINGBOX_PORT}"
        f"?security=none&encryption=none&type=tcp#ТестовыйПериод"
    )
    await message.answer(
        "🔑 Тестовый период активирован!\n\n"
        f"• Ваш ключ: `{link}`\n"
        f"• Действует до: {expires}",
        parse_mode="Markdown"
    )


def register_handlers(dp: Dispatcher):
    dp.message.register(
        trial_handler,
        Text(text="⏳ Тестовый период", ignore_case=True)
    )
