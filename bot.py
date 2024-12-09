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

# Загрузка переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@your_channel_name")
POST_INTERVAL = int(os.environ.get("TELEGRAM_POST_INTERVAL", "60"))  # Пауза между отправками в секундах
FETCH_BATCH_SIZE = int(os.environ.get("FETCH_BATCH_SIZE", "1"))  # Количество тредов за раз
FETCH_DELAY = int(os.environ.get("FETCH_DELAY", "60"))  # Пауза между пакетами в секундах

# Проверка переменных окружения
if not BOT_TOKEN:
    logger.error("Не задан BOT_TOKEN. Завершение работы.")
    raise ValueError("Переменная окружения BOT_TOKEN не задана!")

if not TELEGRAM_CHANNEL_ID:
    logger.error("Не задан TELEGRAM_CHANNEL_ID. Завершение работы.")
    raise ValueError("Переменная окружения TELEGRAM_CHANNEL_ID не задана!")

# Логируем переменные окружения (без BOT_TOKEN для безопасности)
logger.info("Переменные окружения:")
logger.info(f"  TELEGRAM_CHANNEL_ID: {TELEGRAM_CHANNEL_ID}")
logger.info(f"  POST_INTERVAL: {POST_INTERVAL}")
logger.info(f"  FETCH_BATCH_SIZE: {FETCH_BATCH_SIZE}")
logger.info(f"  FETCH_DELAY: {FETCH_DELAY}")

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

