from aiogram import Router, F, types
from aiogram.filters import Command, Filter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func

from bot.config import settings
from bot.services.db import async_session
from bot.models import Location, Trial, Purchase, User

router = Router()

# 👮 Фильтр: только для админов
class IsAdmin(Filter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in self.admin_ids

# 📦 Состояния FSM
class AddLocation(StatesGroup):
    name = State()
    code = State()

class BroadcastState(StatesGroup):
    message = State()

# 🔧 Команда /admin
@router.message(Command("admin"), IsAdmin(settings.ADMIN_IDS))
async def admin_menu(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data="admin_stats")
    kb.button(text="📍 Управление локациями", callback_data="manage_locations")
    kb.button(text="📣 Рассылка", callback_data="broadcast")
    await message.answer("🔧 Панель администратора", reply_markup=kb.as_markup())

# 📊 Статистика
@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: types.CallbackQuery):
    async with async_session() as session:
        trials_count = await session.scalar(select(func.count()).select_from(Trial))
        purchases_count = await session.scalar(select(func.count()).select_from(Purchase))

    text = (
        f"📊 *Статистика*\n\n"
        f"👤 Пользователей с тестом: {trials_count}\n"
        f"💸 Платных покупок: {purchases_count}"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="admin_back")
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.as_markup())

# 📍 Список локаций
@router.callback_query(F.data == "manage_locations")
async def manage_locations(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(Location))
        locations = result.scalars().all()

    kb = InlineKeyboardBuilder()
    for loc in locations:
        status = "✅" if loc.is_active else "❌"
        kb.button(text=f"{status} {loc.name}", callback_data=f"loc_{loc.id}")

    kb.button(text="➕ Добавить локацию", callback_data="add_location")
    kb.button(text="⬅️ Назад", callback_data="admin_back")
    await callback.message.edit_text("📍 Локации:", reply_markup=kb.as_markup())

# ➕ Добавление локации
@router.callback_query(F.data == "add_location")
async def prompt_location_name(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddLocation.name)
    await callback.message.edit_text("📝 Введите название новой локации:")

@router.message(AddLocation.name)
async def ask_location_code(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddLocation.code)
    await message.answer("🔤 Теперь введите короткий код локации (например, `nl`):")

@router.message(AddLocation.code)
async def save_location(message: types.Message, state: FSMContext):
    data = await state.get_data()
    async with async_session() as session:
        session.add(Location(name=data["name"], code=message.text.lower()))
        await session.commit()
    await state.clear()
    await message.answer(f"✅ Локация *{data['name']}* добавлена!", parse_mode="Markdown")

# 🔁 Переключение статуса
@router.callback_query(F.data.startswith("loc_"))
async def toggle_location(callback: types.CallbackQuery):
    loc_id = int(callback.data.split("_")[1])
    async with async_session() as session:
        loc = await session.get(Location, loc_id)
        loc.is_active = not loc.is_active
        await session.commit()
    await manage_locations(callback)

# 📣 Запрос текста рассылки
@router.callback_query(F.data == "broadcast")
async def prompt_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastState.message)
    await callback.message.edit_text("✏️ Введите текст рассылки:")

# ✅ Рассылка
@router.message(BroadcastState.message)
async def send_broadcast(message: types.Message, state: FSMContext):
    await state.clear()
    text = message.text

    async with async_session() as session:
        result = await session.execute(select(User.telegram_id))
        user_ids = result.scalars().all()

    success = 0
    fail = 0
    for uid in user_ids:
        try:
            await message.bot.send_message(chat_id=uid, text=text)
            success += 1
        except Exception:
            fail += 1

    await message.answer(f"📬 Рассылка завершена:\n\n✅ Успешно: {success}\n❌ Ошибки: {fail}")

# ⬅️ Назад
@router.callback_query(F.data == "admin_back")
async def back_to_admin(callback: types.CallbackQuery):
    await admin_menu(callback.message)

# 📥 Регистрация хендлеров
def register_handlers(dp):
    dp.include_router(router)
