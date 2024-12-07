import os
import logging
from multiprocessing import Process
from django.core.management import execute_from_command_line
from telegram_bot.bot import start_bot

# Настройка логирования
logging.basicConfig(
    filename="application.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Установка переменной окружения для Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_chan.settings")

def run_django():
    """Function to run the Django server."""
    try:
        logging.info("Starting Django server...")
        execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"])
    except Exception as e:
        logging.error(f"Error in Django server: {e}")

def run_bot(token):
    """Function to run the Telegram bot."""
    try:
        logging.info("Starting Telegram bot...")
        import asyncio
        asyncio.run(start_bot(token))
    except Exception as e:
        logging.error(f"Error in Telegram bot: {e}")

if __name__ == "__main__":
    logging.info("Starting main application...")

    # Get the bot token from environment variables
    token = os.getenv("BOT_TOKEN")
    if not token:
        logging.error("Telegram bot token is not set! Check environment variables.")
        raise ValueError("Telegram bot token is not set!")

    # Create processes for Django and Telegram bot
    django_process = Process(target=run_django)
    bot_process = Process(target=run_bot, args=(token,))  # Pass the token as an argument

    try:
        # Start the processes
        django_process.start()
        bot_process.start()

        # Wait for both processes to complete
        django_process.join()
        bot_process.join()
    except KeyboardInterrupt:
        logging.info("Shutting down the application...")
        django_process.terminate()
        bot_process.terminate()
    except Exception as e:
        logging.error(f"Error in the main application: {e}")
    finally:
        logging.info("Application has stopped.")
