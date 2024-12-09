# media_handler.py

import asyncio
import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from dvach_service import DvachService
from media_utils import is_url_accessible, create_input_media

logger = logging.getLogger(__name__)

class MediaHandler:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.dvach_service = DvachService()  # Экземпляр DvachService
        self.media_queue = asyncio.Queue()
        self.posted_media = set()

    async def filter_accessible_media(self, media_urls):
        accessible_media = []
        for url in media_urls:
            if await is_url_accessible(url):
                accessible_media.append(url)
            else:
                logger.warning(f"URL недоступен: {url}")
        return accessible_media

    def generate_inline_keyboard(self, thread_url):
        button = InlineKeyboardButton("Перейти в тред", url=thread_url)
        return InlineKeyboardMarkup([[button]])

    async def post_media_group(self):
        while True:
            try:
                media_group = await self.media_queue.get()
                logger.info(f"Отправка медиагруппы: {media_group}")

                # Проверка структуры данных
                if not isinstance(media_group, dict):
                    logger.error("Ошибка: media_group должен быть словарем!")
                    continue

                # Извлечение данных
                media_urls = media_group.get("media", [])
                thread_url = media_group.get("thread_url", "")
                caption = media_group.get("caption", "")

                if not media_urls:
                    logger.warning("Нет доступных медиа для отправки. Пропускаем.")
                    continue

                # Фильтрация доступных медиа
                filtered_media = await self.filter_accessible_media(media_urls)
                if not filtered_media:
                    logger.warning("Нет доступных медиа после фильтрации. Пропускаем.")
                    continue

                # Создание InputMedia объектов
                input_media = [
                    create_input_media(url, caption if i == 0 else None)
                    for i, url in enumerate(filtered_media)
                ]

                # Отправка медиагруппы
                await self.bot.send_media_group(chat_id=self.config.TELEGRAM_CHANNEL_ID, media=input_media)
                await self.bot.send_message(
                    chat_id=self.config.TELEGRAM_CHANNEL_ID,
                    text="Переходите в тред:",
                    reply_markup=self.generate_inline_keyboard(thread_url)
                )
                logger.info("Медиагруппа и кнопка успешно отправлены.")
            except Exception as e:
                logger.error(f"Ошибка при отправке медиагруппы: {e}")
            finally:
                await asyncio.sleep(self.config.POST_INTERVAL)
