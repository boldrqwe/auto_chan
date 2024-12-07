import asyncio
import logging
import os

import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

nest_asyncio.apply()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне ссылку, а я найду с неё ссылки.")

async def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("Не задан токен бота. Установите переменную окружения BOT_TOKEN.")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))


    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
