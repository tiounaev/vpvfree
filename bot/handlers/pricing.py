from telegram import Update
from telegram.ext import ContextTypes

async def pricing_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="💰 Тарифы:\n\n1 день — 30₽\n1 месяц — 300₽\n3 месяца — 800₽\n6 месяцев — 1500₽\n12 месяцев — 2800₽\n\nОплата в разработке.",
        parse_mode="Markdown"
    )
