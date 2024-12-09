# media_poster.py

import logging
import redis
import json
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from media_utils import create_input_media

logger = logging.getLogger(__name__)

class MediaPoster:
    def __init__(self, config):
        self.config = config
        self.bot = config.bot  # Убедитесь, что Bot экземпляр правильно инициализирован
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1)

    def enqueue_media(self, media_group):
        """Добавляет медиагруппу в очередь Redis."""
        try:
            self.redis_client.rpush('media_queue', json.dumps(media_group))
            logger.info("Медиагруппа добавлена в Redis очередь.")
        except Exception as e:
            logger.error(f"Ошибка при добавлении медиагруппы в очередь Redis: {e}")

    def generate_inline_keyboard(self, thread_url):
        button = InlineKeyboardButton("Перейти в тред", url=thread_url)
        return InlineKeyboardMarkup([[button]])

    def post_media_group(self):
        """Отправляет медиагруппы из Redis очереди в Telegram."""
        while True:
            try:
                media_group_json = self.redis_client.blpop('media_queue', timeout=0)[1]
                media_group = json.loads(media_group_json)
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

                # Создание InputMedia объектов
                input_media = [
                    create_input_media(url, caption if i == 0 else None)
                    for i, url in enumerate(media_urls)
                ]

                # Отправка медиагруппы
                self.bot.send_media_group(chat_id=self.config.TELEGRAM_CHANNEL_ID, media=input_media)
                self.bot.send_message(
                    chat_id=self.config.TELEGRAM_CHANNEL_ID,
                    text="Переходите в тред:",
                    reply_markup=self.generate_inline_keyboard(thread_url)
                )
                logger.info("Медиагруппа и кнопка успешно отправлены.")
            except Exception as e:
                logger.error(f"Ошибка при отправке медиагруппы: {e}")
