from pydantic import BaseSettings, validator
from typing import List


class Settings(BaseSettings):
    # 🔐 Токены и доступ
    BOT_TOKEN: str
    TELEGRAM_PAY_PROVIDER_TOKEN: str

    # 📊 Админы и рефералка
    ADMIN_IDS: List[int]
    DEFAULT_REFERRAL_PERCENT: int = 15

    # 🗄️ База данных
    DB_DSN: str

    # 🌐 Sing-box конфигурация
    SINGBOX_HOST: str = "77.110.109.70"
    SINGBOX_PORT: int = 443
    SINGBOX_CONFIG_PATH: str = "/etc/sing-box/config.json"

    # ⏱️ Тестовый период
    TRIAL_DURATION_MINUTES: int = 1

    # 🌍 Временная зона
    TIMEZONE: str = "Europe/Helsinki"

    # 💱 Платёжные настройки
    PAYMENT_CURRENCY: str = "RUB"

    @validator("ADMIN_IDS", pre=True)
    def parse_admin_ids(cls, v):
        """
        Поддержка форматов:
        • "123456789"
        • "123456789,987654321"
        • "[123456789, 987654321]"
        """
        if isinstance(v, str):
            return [int(x) for x in v.strip("[]").split(",") if x.strip()]
        return v

    class Config:
        env_file = ".env"


# 📦 Основной объект настроек
settings = Settings()

# 🔁 Удобные алиасы
DOMAIN = settings.SINGBOX_HOST
PORT = settings.SINGBOX_PORT
