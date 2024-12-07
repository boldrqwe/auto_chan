import os
import threading
from django.core.management import execute_from_command_line
from telegram_bot.bot import start_bot

def run_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])

def run_bot():
    start_bot()

if __name__ == "__main__":
    threading.Thread(target=run_django).start()
    threading.Thread(target=run_bot).start()
