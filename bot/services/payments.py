from aiogram.types import LabeledPrice, PreCheckoutQuery, Message
from aiogram import Bot
from bot.config import settings

class TelegramPayProvider:
    @staticmethod
    def generate_invoice(title: str, description: str, payload: str, prices: list):
        return {
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": settings.TELEGRAM_PAY_PROVIDER_TOKEN,
            "currency": settings.PAYMENT_CURRENCY,
            "prices": prices
        }

async def purchase_handler(message: Message):
    price = LabeledPrice(label="VPN Access", amount=1000)  # 10.00 руб
    invoice = TelegramPayProvider.generate_invoice(
        title="VPN Access",
        description="Purchase VPN subscription",
        payload="vpn_purchase",
        prices=[price]
    )
    await Bot(token=settings.BOT_TOKEN).send_invoice(
        chat_id=message.chat.id,
        **invoice
    )

async def precheckout_handler(query: PreCheckoutQuery):
    await query.answer(ok=True)

async def successful_payment_handler(message: Message):
    await message.reply("Payment received, спасибо!")
