from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 О Проекте", callback_data='about')],
        [InlineKeyboardButton("🧪 Тест-доступ", callback_data='test')],
        [InlineKeyboardButton("💰 Купить доступ", callback_data='buy')],
        [InlineKeyboardButton("📦 Помощь и Связь", callback_data='support')],
    ]
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\nВыберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def register(application):
    application.add_handler(CommandHandler("start", start_command))