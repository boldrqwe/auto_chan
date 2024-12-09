# bot.py
import os
import logging
from celery_app import app

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

def main():
    TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@your_channel_name")
    POST_INTERVAL = int(os.environ.get("TELEGRAM_POST_INTERVAL", "10"))

    logger.info("Запуск бота и планировщика задач...")
    # Celery Beat автоматически запустит `job_collect_media` каждые 60 секунд

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки. Завершаем работу...")
    except Exception as e:
        logger.exception("Критическая ошибка в работе бота: %s", e)
