import os
import logging
from telegram import Bot

logger = logging.getLogger(__name__)

class BotConfig:
    def __init__(self):
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
        self.POST_INTERVAL = int(os.getenv("TELEGRAM_POST_INTERVAL", "50"))
        self.FETCH_BATCH_SIZE = int(os.getenv("FETCH_BATCH_SIZE", "1"))
        self.FETCH_DELAY = int(os.getenv("FETCH_DELAY", "50"))

        # Проверка переменных окружения
        self.validate_environment()

    def validate_environment(self):
        if not self.BOT_TOKEN:
            logger.error("Не задан BOT_TOKEN. Завершение работы.")
            raise ValueError("Переменная окружения BOT_TOKEN не задана!")

        if not self.TELEGRAM_CHANNEL_ID:
            logger.error("Не задан TELEGRAM_CHANNEL_ID. Завершение работы.")
            raise ValueError("Переменная окружения TELEGRAM_CHANNEL_ID не задана!")

        logger.info("Переменные окружения успешно загружены.")

    async def check_chat_access(self, bot: Bot):
        try:
            logger.info(f"Проверка доступа к чату: {self.TELEGRAM_CHANNEL_ID}")
            chat = await bot.get_chat(chat_id=self.TELEGRAM_CHANNEL_ID)
            logger.info(f"Бот имеет доступ к чату: {chat.title}")
        except Exception as e:
            logger.error(f"Ошибка доступа к чату {self.TELEGRAM_CHANNEL_ID}: {e}")
            raise ValueError("Невозможно получить доступ к указанному чату!")
