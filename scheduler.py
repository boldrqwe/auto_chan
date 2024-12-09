# scheduler.py

import asyncio
import logging
from tasks import collect_media_task, post_media_task

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, media_handler, config):
        self.media_handler = media_handler
        self.config = config

    def start(self):
        asyncio.create_task(self.media_handler.post_media_group())
        asyncio.create_task(self.schedule_job())

    async def schedule_job(self):
        while True:
            logger.info("Запуск плановой задачи по сбору медиа...")
            collect_media_task.delay()  # Запускаем Celery задачу
            await asyncio.sleep(self.config.FETCH_DELAY)
