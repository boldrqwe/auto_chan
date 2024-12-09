# bot.py

import asyncio
import logging
from telegram.ext import ApplicationBuilder
from config import BotConfig
from media_handler import MediaHandler
from scheduler import Scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

async def main():
    config = BotConfig()  # Загружаем конфигурацию
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Проверяем доступ к чату
    await config.check_chat_access(application.bot)

    # Создаем обработчик медиа
    media_handler = MediaHandler(application.bot, config)

    # Инициализируем планировщик
    scheduler = Scheduler(media_handler, config)
    scheduler.start()

    # Запускаем бота
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки. Завершаем работу...")
    except Exception as e:
        logger.exception("Критическая ошибка в работе бота: %s", e)
