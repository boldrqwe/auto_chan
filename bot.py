# bot.py
import os
import logging
import asyncio
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
POST_INTERVAL = int(os.environ.get("TELEGRAM_POST_INTERVAL", "10"))  # Пауза между отправками в секундах
FETCH_BATCH_SIZE = int(os.environ.get("FETCH_BATCH_SIZE", "5"))  # Количество тредов за раз
FETCH_DELAY = int(os.environ.get("FETCH_DELAY", "45"))  # Пауза между пакетами в секундах

if not BOT_TOKEN:
    logger.error("Не задан BOT_TOKEN, завершение работы.")
    raise ValueError("Не задан BOT_TOKEN")

application = ApplicationBuilder().token(BOT_TOKEN).build()
bot: Bot = application.bot

dvach = DvachService()
posted_media = set()
media_queue = asyncio.Queue()

def scheduled_job():
    logger.info("Запуск плановой задачи по сбору медиа...")
    asyncio.create_task(job_collect_media(dvach, posted_media, media_queue, FETCH_BATCH_SIZE, FETCH_DELAY))

async def main():
    logger.info("Запуск бота...")
    asyncio.create_task(post_media_from_queue(bot, TELEGRAM_CHANNEL_ID, POST_INTERVAL, media_queue))

    # Запускаем задачу сбора медиа каждые 1 минуту
    while True:
        scheduled_job()
        await asyncio.sleep(60)  # Ждём 60 секунд перед следующим сбором

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки. Завершаем работу...")
    except Exception as e:
        logger.exception("Критическая ошибка в работе бота: %s", e)
