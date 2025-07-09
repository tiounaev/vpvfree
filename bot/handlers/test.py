from telegram import Update
from telegram.ext import ContextTypes
from database import add_user, has_received_test, mark_test_given

async def test_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    if has_received_test(user_id):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ Вы уже получали тест-доступ.")
        return

    test_key = "vless://example-test-key"

    mark_test_given(user_id)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"✅ Ваш тест-доступ:\n\n`{test_key}`", parse_mode="Markdown")
