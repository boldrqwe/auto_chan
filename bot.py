import os
import logging
import asyncio
import schedule
import nest_asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder

from dvach_service import DvachService
from tasks import job_collect_media, post_media_from_queue

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

nest_asyncio.apply()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@your_channel_name")
POST_INTERVAL = int(os.environ.get("TELEGRAM_POST_INTERVAL", "10"))

if not BOT_TOKEN:
    logger.error("Не задан BOT_TOKEN, завершение работы.")
    raise ValueError("Не задан BOT_TOKEN")

application = ApplicationBuilder().token(BOT_TOKEN).build()
bot: Bot = application.bot

dvach = DvachService()
posted_media = set()
media_queue = []

def scheduled_job():
    logger.info("Запуск плановой задачи по сбору медиа...")
    job_collect_media(dvach, posted_media, media_queue)

async def main():
    logger.info("Запуск бота...")
    asyncio.create_task(post_media_from_queue(bot, TELEGRAM_CHANNEL_ID, POST_INTERVAL, media_queue))

    schedule.every(1).minutes.do(scheduled_job)

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки. Завершаем работу...")
    except Exception as e:
        logger.exception("Критическая ошибка в работе бота: %s", e)
