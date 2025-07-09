import uuid
import json
import base64
import subprocess
import logging
from pathlib import Path

from aiogram import Bot
from bot.config import settings
from bot.database import mark_test_given

# Настройки
DOMAIN = settings.SINGBOX_HOST
PORT = settings.SINGBOX_PORT
BOT_TOKEN = settings.BOT_TOKEN
CONFIG_PATH = Path(settings.SINGBOX_CONFIG_PATH)

# Telegram-бот
bot = Bot(token=BOT_TOKEN)

# Логгер
logger = logging.getLogger(__name__)


# 🔔 Отправка уведомления пользователю
async def send_message_to_user(user_id: int, text: str):
    try:
        await bot.send_message(chat_id=user_id, text=text)
        logger.info(f"[generator] Уведомление отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(f"[generator] Ошибка при отправке уведомления {user_id}: {e}")


# 📄 Работа с config.json
def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(conf):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=2)

    try:
        subprocess.run(["systemctl", "restart", "sing-box"], check=True)
        logger.info("[generator] sing-box успешно перезапущен через systemctl")
    except FileNotFoundError:
        logger.warning("[generator] systemctl не найден — пробуем через touch")
        try:
            CONFIG_PATH.touch()
            logger.info("[generator] Выполнен touch для обновления конфига")
        except Exception as e:
            logger.error(f"[generator] Ошибка при touch: {e}")
    except subprocess.CalledProcessError as e:
        logger.error(f"[generator] Ошибка при перезапуске sing-box: {e}")


def gen_uuid() -> str:
    return str(uuid.uuid4())


def _add_user(proto: str, user_obj: dict):
    conf = load_config()
    for inbound in conf.get("inbounds", []):
        if inbound.get("type") == proto:
            if "users" in inbound:
                inbound["users"].append(user_obj)
            else:
                inbound["password"] = user_obj["password"]
            break
    save_config(conf)


# 🔑 Генераторы протоколов
def generate_vless(user_id: int) -> str:
    uid = gen_uuid()
    _add_user("vless", {"uuid": uid, "flow": "xtls-rprx-vision"})
    link = f"vless://{uid}@{DOMAIN}:443?encryption=none&security=reality"
    mark_test_given(user_id, "vless")
    return link


def generate_trojan(user_id: int) -> str:
    pwd = gen_uuid()
    _add_user("trojan", {"password": pwd})
    link = f"trojan://{pwd}@{DOMAIN}:8443?security=tls"
    mark_test_given(user_id, "trojan")
    return link


def generate_hysteria(user_id: int) -> str:
    pwd = gen_uuid()
    _add_user("hysteria", {"password": pwd})
    link = f"hysteria://{pwd}@{DOMAIN}:8888?insecure=1"
    mark_test_given(user_id, "hysteria")
    return link


def generate_shadowsocks(user_id: int) -> str:
    pwd = gen_uuid()[:16]
    _add_user("shadowsocks", {"_dummy": True, "password": pwd})
    userinfo = f"2022-blake3-aes-128-gcm:{pwd}".encode()
    encoded = base64.urlsafe_b64encode(userinfo).decode()
    link = f"ss://{encoded}@{DOMAIN}:8388"
    mark_test_given(user_id, "shadowsocks")
    return link


def generate_vmess(user_id: int) -> str:
    uid = gen_uuid()
    _add_user("vmess", {"id": uid, "alterId": 0, "security": "auto"})
    vmess_config = {
        "v": "2", "ps": "test", "add": DOMAIN, "port": "10086",
        "id": uid, "aid": "0", "net": "tcp", "type": "none", "tls": "tls"
    }
    encoded = base64.urlsafe_b64encode(json.dumps(vmess_config).encode()).decode()
    link = f"vmess://{encoded}"
    mark_test_given(user_id, "vmess")
    return link


def generate_tuic(user_id: int) -> str:
    pwd = gen_uuid()
    _add_user("tuic", {"password": pwd})
    link = f"tuic://{pwd}@{DOMAIN}:9000"
    mark_test_given(user_id, "tuic")
    return link
