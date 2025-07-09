#!/usr/bin/env python3
from telegram.ext import Application
from config import BOT_TOKEN
from database import init_db
from handlers import start, callbacks

def main():
    # Инициализация базы данных
    init_db()

    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    start.register(application)
    callbacks.register(application)

    print("Бот запущен...")
    # Запускаем polling (блокирующий вызов)
    application.run_polling()

if __name__ == '__main__':
    main()
