# handlers/buy.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

PROTOCOLS = ["vless", "shadowsocks", "hysteria"]
DURATIONS = {
    "1d": "1 день",
    "1m": "1 месяц",
    "3m": "3 месяца",
    "6m": "6 месяцев",
    "12m": "12 месяцев"
}

async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton(proto.upper(), callback_data=f"buy_proto_{proto}")]
        for proto in PROTOCOLS
    ]
    keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="start")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.answer()
    await query.edit_message_text("Выберите протокол для покупки:", reply_markup=reply_markup)

async def choose_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    proto = query.data.replace("buy_proto_", "")
    context.user_data["buy_proto"] = proto

    keyboard = [
        [InlineKeyboardButton(label, callback_data=f"buy_duration_{code}")]
        for code, label in DURATIONS.items()
    ]
    keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="buy")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.edit_message_text(
        f"Выбран протокол: {proto.upper()}\n\nТеперь выберите срок:",
        reply_markup=reply_markup
    )

async def confirm_fake_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    duration = query.data.replace("buy_duration_", "")
    proto = context.user_data.get("buy_proto")

    await query.answer()
    await query.edit_message_text(
        f"🛒 Вы выбрали:\nПротокол: {proto.upper()}\nСрок: {DURATIONS[duration]}\n\n💳 Оплата появится скоро!"
    )

def register(application):
    application.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy$"))
    application.add_handler(CallbackQueryHandler(choose_duration, pattern="^buy_proto_"))
    application.add_handler(CallbackQueryHandler(confirm_fake_purchase, pattern="^buy_duration_"))
