import logging

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    filename="bot.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Обработчик команды /start
async def start_command(update, context):
    user = update.effective_user
    logging.info(f"Received /start command from user_id={user.id}, username={user.username}")
    await update.message.reply_text("Hello! I'm your bot. Send me a message, and I'll echo it.")


# Обработчик всех текстовых сообщений
async def echo_message(update, context):
    message = update.message.text
    user_id = update.effective_user.id
    logging.info(f"Message from user_id={user_id}: {message}")
    await update.message.reply_text(f"You said: {message}")


# Основная функция запуска бота
async def start_bot(token):
    logging.info("Starting Telegram bot...")

    if not token:
        logging.error("Telegram bot token is not set!")
        raise ValueError("Telegram bot token is not set!")

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))

    try:
        logging.info("Bot is running...")
        # Запускаем асинхронно бота
        await application.run_polling()
    except Exception as e:
        logging.error(f"Error occurred while running Telegram bot: {e}")
        # Не вызывайте здесь application.shutdown(), run_polling сам позаботится о корректной остановке
    finally:
        logging.info("Telegram bot stopped.")

