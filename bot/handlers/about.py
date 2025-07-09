from telegram import Update
from telegram.ext import ContextTypes

async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="🔹 *О проекте*\n\nМы предлагаем безопасный и быстрый VPN-доступ через протоколы Sing-box, включая VLESS Reality, Shadowsocks и другие.",
        parse_mode="Markdown"
    )
