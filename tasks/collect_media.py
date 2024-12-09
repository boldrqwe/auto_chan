# tasks/collect_media.py

import logging
from celery import shared_task
from dvach_service import DvachService
from harkach_markup_converter import HarkachMarkupConverter
from media_poster import MediaPoster
from config import BotConfig

logger = logging.getLogger(__name__)

@shared_task(name='tasks.collect_media_task')
def collect_media_task():
    """Celery задача для сбора медиа с 2ch."""
    config = BotConfig()
    dvach = DvachService()
    converter = HarkachMarkupConverter()
    media_poster = MediaPoster(config)

    try:
        threads = dvach.fetch_threads(board="b")
        logger.info(f"Получено {len(threads)} тредов.")
    except Exception as e:
        logger.error(f"Не удалось получить треды: {e}")
        return

    for thread in threads:
        thread_num = thread.get("num") or thread.get("thread_num")
        if not thread_num:
            logger.debug(f"Пропускаем тред без номера: {thread}")
            continue

        try:
            thread_data = dvach.fetch_thread_data(thread_num, board="b")
        except Exception as e:
            logger.error(f"Не удалось получить данные треда {thread_num}: {e}")
            continue

        if not thread_data or not thread_data.get("media"):
            logger.debug(f"Тред {thread_num} не содержит медиа.")
            continue

        # Обработка медиа
        caption_html = converter.convert_to_tg_html(thread_data.get("caption", "")[:1024])
        media_urls = thread_data["media"]

        media_group = {
            "thread_url": f"https://2ch.hk/b/res/{thread_num}.html",
            "caption": caption_html,
            "media": media_urls
        }

        # Добавляем в очередь для отправки
        media_poster.enqueue_media(media_group)

    logger.info("Сбор медиа завершен.")
