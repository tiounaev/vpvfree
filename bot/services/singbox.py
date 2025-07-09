import json
import logging
import subprocess
from filelock import FileLock
from bot.config import settings


def add_user(params: dict) -> bool:
    """
    Добавляет нового пользователя в config.json
    """
    lock_path = settings.SINGBOX_CONFIG_PATH + ".lock"
    lock = FileLock(lock_path)

    try:
        with lock:
            logging.info(f"[singbox.py] add_user called with params: {params}")

            with open(settings.SINGBOX_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            new_user = {
                "name": f"user_{params['uuid'][:6]}",
                "uuid": params["uuid"],
                "flow": params.get("flow", "")
            }

            existing_uuids = [u["uuid"] for u in data["inbounds"][0].get("users", [])]
            if new_user["uuid"] in existing_uuids:
                logging.info(f"[singbox.py] UUID {new_user['uuid']} уже есть в config.json")
                return True

            data["inbounds"][0]["users"].append(new_user)
            logging.info(f"[singbox.py] Добавлен новый пользователь: {new_user}")

            with open(settings.SINGBOX_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        logging.error(f"[singbox.py] Ошибка при добавлении пользователя: {e}")
        return False

    return _restart_singbox()


def remove_user(uuid: str) -> bool:
    """
    Удаляет пользователя по uuid из config.json
    """
    lock_path = settings.SINGBOX_CONFIG_PATH + ".lock"
    lock = FileLock(lock_path)

    try:
        with lock:
            logging.info(f"[singbox.py] remove_user called for uuid: {uuid}")

            with open(settings.SINGBOX_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            original_count = len(data["inbounds"][0].get("users", []))
            data["inbounds"][0]["users"] = [
                user for user in data["inbounds"][0]["users"]
                if user.get("uuid") != uuid
            ]
            new_count = len(data["inbounds"][0]["users"])

            if new_count == original_count:
                logging.warning(f"[singbox.py] UUID {uuid} не найден — ничего не удалено")
                return False

            with open(settings.SINGBOX_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logging.info(f"[singbox.py] Удален пользователь с uuid {uuid}")

    except Exception as e:
        logging.error(f"[singbox.py] Ошибка при удалении пользователя: {e}")
        return False

    return _restart_singbox()


def _restart_singbox() -> bool:
    """
    Перезапускает sing-box (через systemctl, с sudo если надо)
    """
    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "sing-box"],
            check=True
        )
        logging.info("[singbox.py] sing-box успешно перезапущен")
        return True

    except FileNotFoundError:
        logging.warning("[singbox.py] systemctl не найден — пропускаем перезапуск sing-box")
    except subprocess.CalledProcessError as e:
        logging.warning(f"[singbox.py] Не удалось перезапустить sing-box: {e}")

    return False
