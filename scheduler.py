import asyncio
import logging
from tasks import job_collect_media

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, media_handler, config):
        self.media_handler = media_handler
        self.config = config

    def start(self):
        asyncio.create_task(self.media_handler.post_media())
        asyncio.create_task(self.schedule_job())

    async def schedule_job(self):
        while True:
            logger.info("Запуск плановой задачи по сбору медиа...")
            asyncio.create_task(job_collect_media(
                self.media_handler.posted_media,
                self.media_handler.media_queue,
                self.config.FETCH_BATCH_SIZE,
                self.config.FETCH_DELAY
            ))
            await asyncio.sleep(self.config.FETCH_DELAY)
