from telegram.ext import ApplicationBuilder, CommandHandler
from .handlers import start_command
import os

def start_bot():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("Не задан токен Telegram-бота. Проверьте переменные окружения!")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.run_polling()

