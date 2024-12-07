import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# Настраиваем логирование
logging.basicConfig(
    filename="application.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def start_command(update, context):
    await update.message.reply_text("Hello! I'm a Telegram bot.")

async def start_bot(token):
    logging.info("Starting Telegram bot...")
    if not token:
        logging.error("Telegram bot token is not set!")
        raise ValueError("Telegram bot token is not set!")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start_command))

    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
    except Exception as e:
        logging.error(f"Error occurred while running Telegram bot: {e}")
    finally:
        await application.stop()
