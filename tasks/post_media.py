# tasks/post_media.py

import logging
from celery import shared_task
from media_poster import MediaPoster
from config import BotConfig

logger = logging.getLogger(__name__)

@shared_task(name='tasks.post_media_task')
def post_media_task():
    """Celery задача для отправки медиагрупп в Telegram."""
    config = BotConfig()
    media_poster = MediaPoster(config)

    try:
        media_poster.post_media_group()
    except Exception as e:
        logger.error(f"Ошибка при отправке медиагруппы: {e}")
