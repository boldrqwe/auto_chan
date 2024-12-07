from telegram.ext import ApplicationBuilder, CommandHandler
import os

async def start_command(update, context):
    await update.message.reply_text("Привет! Я Telegram-бот.")

async def start_bot():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("Не задан токен Telegram-бота. Проверьте переменные окружения!")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start_command))

    # Запуск бота
    await application.run_polling()
