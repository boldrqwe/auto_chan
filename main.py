import os
import asyncio
from django.core.management import execute_from_command_line
from telegram_bot.bot import start_bot  # Импорт вашей функции запуска бота

# Установим настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_chan.settings")


async def run_django():
    """Запускает Django-сервер в asyncio."""
    await asyncio.to_thread(
        execute_from_command_line,
        ["manage.py", "runserver", "127.0.0.1:8000"]
    )


async def main():
    """Запускает Django и Telegram-бота параллельно."""
    # Запускаем Django и бота как задачи
    await asyncio.gather(run_django(), start_bot())


if __name__ == "__main__":
    # Запускаем основную функцию через asyncio
    asyncio.run(main())

