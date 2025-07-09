# handlers/help.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

HELP_TEXT = """
📥 <b>Как начать пользоваться?</b>

1. Скачайте приложение:
• Android: <a href="https://play.google.com/store/apps/details?id=com.github.v2ray.v2rayNG">v2rayNG</a>
• iOS: <a href="https://apps.apple.com/app/shadowrocket/id932747118">Shadowrocket</a>
• Windows/macOS: <a href="https://github.com/SagerNet/sing-box/releases">Sing-box</a>

2. Импортируйте полученный конфиг (через QR или ссылку)

3. Подключитесь и пользуйтесь!

📨 <b>Возникли вопросы?</b>
Свяжитесь с нами: @YourSupportUsername
"""

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("⬅ Назад", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.answer()
    await query.edit_message_text(
        HELP_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )

def register(application):
    application.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
