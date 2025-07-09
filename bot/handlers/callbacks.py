from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import add_user, has_received_test, mark_test_given
from generator import (
    generate_vless, generate_vmess, generate_trojan,
    generate_shadowsocks, generate_hysteria, generate_tuic
)
from datetime import datetime, timedelta

MAIN_TEXT = "👋 Добро пожаловать!\n\nВыберите действие из меню ниже:"
MAIN_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧠 О Проекте", callback_data='about')],
    [InlineKeyboardButton("🧪 Тест-доступ", callback_data='test')],
    [InlineKeyboardButton("💰 Купить доступ", callback_data='buy')],
    [InlineKeyboardButton("📦 Помощь и Связь", callback_data='support')],
])

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    add_user(user_id)

    # О проекте
    if query.data == "about":
        await query.edit_message_text(
            text=(
                "🔹 *О проекте*\n\n"
                "Быстрый и безопасный VPN на основе Sing-box с поддержкой:\n"
                "- VLESS + Reality\n"
                "- VMess\n"
                "- Trojan\n"
                "- Shadowsocks\n"
                "- Hysteria\n"
                "- TUIC\n\n"
                "🥇 Тест-доступ на 12 часов.\n"
                "💸 Тарифы: 1д–50₽,1м–300₽ и т.д."
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back")]])
        )
        return

    # Меню тест-доступа
    if query.data == "test":
        buttons = []
        for proto, label in [
            ("vless","VLESS"),("vmess","VMess"),
            ("trojan","Trojan"),("shadowsocks","Shadowsocks"),
            ("hysteria","Hysteria"),("tuic","TUIC")
        ]:
            if not has_received_test(user_id, proto):
                buttons.append([InlineKeyboardButton(label, callback_data=f"get_{proto}")])
        if not buttons:
            await query.edit_message_text(
                "⛔ Все тестовые ключи уже выданы.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back")]])
            )
        else:
            buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
            await query.edit_message_text(
                "Выберите протокол для тест-доступа:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        return

    # Выдача тестовых ключей
    mapping = {
        "vless":    generate_vless,
        "vmess":    generate_vmess,
        "trojan":   generate_trojan,
        "shadowsocks": generate_shadowsocks,
        "hysteria": generate_hysteria,
        "tuic":     generate_tuic,
    }
    for proto, gen in mapping.items():
        if query.data == f"get_{proto}":
            if has_received_test(user_id, proto):
                await query.edit_message_text(f"❗ Тест {proto.upper()} уже выдан.")
            else:
                link = gen(user_id)  # <-- передаём user_id!
                expire = datetime.utcnow() + timedelta(hours=12)
                text = (
                    f"🧪 *{proto.upper()}* (12 ч)\n\n"
                    f"`{link}`\n\n"
                    f"⌛ Действует до _{expire.strftime('%Y-%m-%d %H:%M UTC')}_"
                )
                await query.edit_message_text(
                    text=text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back")]])
                )
            return

    # Тарифы
    if query.data == "buy":
        await query.edit_message_text(
            text=(
                "💰 *Тарифы*\n\n"
                "1 день — 50₽\n"
                "1 месяц — 300₽\n"
                "3 месяца — 750₽\n"
                "6 месяцев — 1400₽\n"
                "12 месяцев — 2500₽"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back")]])
        )
        return

    # Помощь
    if query.data == "support":
        await query.edit_message_text(
            text=(
                "📦 *Помощь и связь*\n\n"
                "• Скачать клиент: https://github.com/SagerNet/sing-box\n"
                "• Документация и примеры конфигов\n\n"
                "📬 Поддержка: @YourSupportUsername"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back")]])
        )
        return

    # Назад в меню
    if query.data == "back":
        await query.edit_message_text(text=MAIN_TEXT, reply_markup=MAIN_KB)

def register(application):
    application.add_handler(CallbackQueryHandler(handle_callback))
