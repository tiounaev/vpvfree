from aiogram import Router, types, F, Bot, Dispatcher
from aiogram.filters import Text
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from bot.config import settings
from bot.services.db import async_session
from bot.models import Location, Tariff

router = Router()

# 1️⃣ Кнопка "Купить VPN"
@router.message(Text(text="🛒 Купить VPN"))
async def choose_location(message: types.Message):
    async with async_session() as session:
        result = await session.execute(select(Location).where(Location.is_active == True))
        locations = result.scalars().all()

    if not locations:
        await message.answer("⛔️ Нет доступных локаций.")
        return

    kb = InlineKeyboardBuilder()
    for loc in locations:
        kb.button(text=loc.name, callback_data=f"buy_loc:{loc.id}")
    await message.answer("🌍 Выберите локацию:", reply_markup=kb.as_markup())

# 2️⃣ Пользователь выбрал локацию
@router.callback_query(F.data.startswith("buy_loc:"))
async def show_tariffs(callback: types.CallbackQuery):
    location_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        result = await session.execute(
            select(Tariff).where(Tariff.location_id == location_id)
        )
        tariffs = result.scalars().all()

    if not tariffs:
        await callback.answer("⛔️ Для этой локации нет тарифов.", show_alert=True)
        return

    kb = InlineKeyboardBuilder()
    for tariff in tariffs:
        kb.button(
            text=tariff.title,
            callback_data=f"buy_tariff:{tariff.id}"
        )
    await callback.message.edit_text("💳 Выберите тариф:", reply_markup=kb.as_markup())

# 3️⃣ Пользователь выбрал тариф — отправляем счёт
@router.callback_query(F.data.startswith("buy_tariff:"))
async def send_invoice(callback: types.CallbackQuery, bot: Bot):
    tariff_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        tariff = await session.get(Tariff, tariff_id)

    if not tariff:
        await callback.answer("Тариф не найден.", show_alert=True)
        return

    prices = [LabeledPrice(label=tariff.title, amount=int(tariff.price * 100))]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Оплата VPN",
        description=tariff.title,
        payload=f"tariff_{tariff.id}",
        provider_token=settings.TELEGRAM_PAY_PROVIDER_TOKEN,
        currency=settings.PAYMENT_CURRENCY,
        prices=prices,
        start_parameter="vpn-bot",
    )
    await callback.answer()

# 4️⃣ Предчекаут
@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(query.id, ok=True)

# 5️⃣ Успешная оплата
@router.message(F.successful_payment)
async def payment_success(message: Message):
    await message.answer("✅ Оплата прошла успешно!\nДоступ будет активирован в ближайшее время.")

# 6️⃣ Регистрация
def register_handlers(dp: Dispatcher):
    dp.include_router(router)
