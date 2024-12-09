# scheduler.py

import asyncio
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, media_handler, config):
        self.media_handler = media_handler
        self.config = config

    def start(self):
        # Запускаем внутренние асинхронные задачи, если необходимо
        asyncio.create_task(self.media_handler.post_media_group())
        logger.info("Scheduler запущен и запустил post_media_group.")
