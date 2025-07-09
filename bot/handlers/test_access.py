# handlers/test_access.py
import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

DATA_FILE = "test_users.json"
PROTOCOLS = ["vless", "shadowsocks", "hysteria"]

# Инициализация базы, если не существует
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def test_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = load_data()

    keyboard = []
    for proto in PROTOCOLS:
        used = proto in data.get(user_id, [])
        label = f"{proto.upper()} ✅" if used else proto.upper()
        keyboard.append([InlineKeyboardButton(label, callback_data=f"test_{proto}")])

    keyboard.append([InlineKeyboardButton("⬅ Назад", callback_data="start")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()
    await query.edit_message_text("Выберите протокол для теста (1 раз для каждого):", reply_markup=reply_markup)

async def handle_protocol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = load_data()
    protocol = query.data.replace("test_", "")

    used = data.get(user_id, [])
    if protocol in used:
        await query.answer("Вы уже получили тест этого протокола!", show_alert=True)
    else:
        used.append(protocol)
        data[user_id] = used
        save_data(data)

        # Здесь вставь генерацию конфигов или ссылок
        await query.answer()
        await query.edit_message_text(
            f"✅ Тестовый доступ к {protocol.upper()} выдан!\n(срок: 12 часов)\n\n🔗 [Пример ссылки]()", 
            parse_mode="Markdown"
        )

def register(application):
    application.add_handler(CallbackQueryHandler(test_callback, pattern="^test$"))
    for proto in PROTOCOLS:
        application.add_handler(CallbackQueryHandler(handle_protocol, pattern=f"^test_{proto}$"))
