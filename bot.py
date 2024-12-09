import os
import logging
import asyncio
import nest_asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder
from media_utils import create_input_media
from dvach_service import DvachService
from tasks import job_collect_media
import httpx

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
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "-1002162401416")
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

# Логируем переменные окружения
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

async def is_url_accessible(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка проверки URL {url}: {e}")
        return False

async def filter_accessible_media(media_group):
    accessible_media = []
    for media in media_group:
        if await is_url_accessible(media.media):
            accessible_media.append(media)
        else:
            logger.warning(f"URL недоступен: {media.media}")
    return accessible_media

async def post_media_from_queue(bot, channel_id, interval, media_queue):
    while True:
        try:
            media_group = await media_queue.get()
            logger.info(f"Отправка медиагруппы: {media_group}")

            # Фильтрация доступных ссылок
            filtered_media_group = await filter_accessible_media(media_group)
            if not filtered_media_group:
                logger.warning("Нет доступных медиа для отправки. Пропускаем группу.")
                continue

            # Отправка медиагруппы
            await bot.send_media_group(chat_id=channel_id, media=filtered_media_group)
            logger.info("Медиагруппа успешно отправлена.")

        except Exception as e:
            logger.error(f"Ошибка при отправке медиагруппы: {e}")
        finally:
            await asyncio.sleep(interval)

async def check_chat_access(bot, channel_id):
    try:
        logger.info(f"Проверка доступа к чату: {channel_id}")
        chat = await bot.get_chat(chat_id=channel_id)
        logger.info(f"Бот имеет доступ к чату: {chat.title}")
    except Exception as e:
        logger.error(f"Ошибка доступа к чату {channel_id}: {e}")
        raise ValueError("Невозможно получить доступ к указанному чату!")

async def main():
    logger.info("Запуск бота...")
    await check_chat_access(bot, TELEGRAM_CHANNEL_ID)
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
