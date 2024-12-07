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
    """Функция для запуска Django-сервера."""
    try:
        logging.info("Starting Django server...")
        execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"])
    except Exception as e:
        logging.error(f"Error in Django server: {e}")

def run_bot_process(token):
    """Функция для запуска Telegram-бота."""
    try:
        logging.info("Starting Telegram bot process...")
        import asyncio
        asyncio.run(start_bot(token))
    except Exception as e:
        logging.error(f"Error in Telegram bot process: {e}")

if __name__ == "__main__":
    logging.info("Starting main application...")

    # Получаем токен бота из переменных окружения
    token = os.getenv("BOT_TOKEN")
    if not token:
        logging.error("Telegram bot token is not set! Check environment variables.")
        raise ValueError("Telegram bot token is not set!")

    # Создаём процессы для Django и Telegram-бота
    django_process = Process(target=run_django)
    bot_process = Process(target=run_bot_process, args=(token,))  # Передаём токен как аргумент

    try:
        # Запускаем процессы
        django_process.start()
        bot_process.start()

        # Ожидаем завершения обоих процессов
        django_process.join()
        bot_process.join()
    except KeyboardInterrupt:
        logging.info("Shutting down the application...")
        django_process.terminate()
        bot_process.terminate()
    except Exception as e:
        logging.error(f"Error in main application: {e}")
    finally:
        logging.info("Application has stopped.")
