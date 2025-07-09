from telegram import Update
from telegram.ext import ContextTypes

async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="📦 *Помощь и связь*\n\n1. Скачать клиенты: v2rayNG, Shadowrocket и др.\n2. Импортируйте ссылку\n3. Связь: @your_support_username",
        parse_mode="Markdown"
    )
