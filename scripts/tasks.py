# tasks.py
import logging
from celery import Celery
from media_utils import create_input_media
from harkach_markup_converter import HarkachMarkupConverter
from dvach_service import DvachService
from telegram import Bot
from telegram.error import RetryAfter

# Инициализация Celery
app = Celery('tasks')
app.config_from_object('celery_app')

logger = logging.getLogger(__name__)

converter = HarkachMarkupConverter()
dvach = DvachService()
posted_media = set()

@app.task(bind=True, max_retries=5)
def job_collect_media(self, TELEGRAM_CHANNEL_ID, POST_INTERVAL):
    """Сбор медиа раз в минуту."""
    logger.info("Начинаем сбор медиа с Двача...")
    media_queue = []

    try:
        threads = dvach.fetch_threads(board="b")
        logger.info("Получено %d тредов.", len(threads))
    except Exception as e:
        logger.error(f"Не удалось получить треды: {e}")
        return

    threads_processed = 0
    media_found = 0

    for t in threads:
        thread_num = t.get("num") or t.get("thread_num")
        if not thread_num:
            logger.debug(f"Пропускаем тред без номера: {t}")
            continue
        try:
            t_data = dvach.fetch_thread_data(thread_num, board="b")
        except Exception as e:
            logger.error(f"Не удалось получить данные треда {thread_num}: {e}")
            continue

        if not t_data:
            logger.debug("Нет данных о треде %s (либо пустой)", thread_num)
            continue

        new_media = [m for m in t_data["media"] if m not in posted_media]
        if not new_media:
            logger.debug("Нет новых медиа в треде %s.", thread_num)
            continue

        for m_url in new_media:
            posted_media.add(m_url)

        # Преобразуем caption
        caption_html = converter.convert_to_tg_html(t_data["caption"][:1024])

        # Разбиваем медиа на группы по 10 штук
        batch_size = 10
        media_groups = []
        for i in range(0, len(new_media), batch_size):
            batch = new_media[i:i+batch_size]
            group = []
            for idx, u in enumerate(batch):
                # Только первый элемент первой группы с подписью
                if i == 0 and idx == 0:
                    group.append(create_input_media(u, caption=caption_html))
                else:
                    group.append(create_input_media(u))
            media_groups.append(group)

        for g in media_groups:
            media_queue.append(g)
            media_found += len(g)

        threads_processed += 1
        logger.info("Тред %s обработан. Новых медиа: %d, групп: %d.",
                    thread_num, len(new_media), len(media_groups))

    logger.info("Сбор медиа завершен. Обработано тредов: %d, найдено медиа: %d, очередь размером: %d",
                threads_processed, media_found, len(media_queue))

    # Отправка медиагрупп
    for media_group in media_queue:
        send_media_group.delay(TELEGRAM_CHANNEL_ID, media_group, POST_INTERVAL)

@app.task(bind=True, max_retries=5)
def send_media_group(self, TELEGRAM_CHANNEL_ID, media_group, POST_INTERVAL):
    """Отправка медиагруппы в Telegram."""
    logger.info("Отправка медиагруппы из очереди: %s", [m.media for m in media_group])
    try:
        bot = Bot(token=os.environ.get("BOT_TOKEN"))
        bot.send_media_group(chat_id=TELEGRAM_CHANNEL_ID, media=media_group, parse_mode='HTML')
        logger.info("Медиагруппа успешно отправлена.")
        time.sleep(POST_INTERVAL)  # Пауза между отправками
    except RetryAfter as e:
        wait_time = e.retry_after
        logger.error(f"Flood control exceeded. Подождем {wait_time} секунд, затем повторим.")
        self.retry(countdown=wait_time)
        # Возвращаем медиагруппу обратно в очередь
        send_media_group.delay(TELEGRAM_CHANNEL_ID, media_group, POST_INTERVAL)
    except Exception as e:
        logger.error(f"Ошибка при отправке медиагруппы: {e}")
        self.retry(exc=e, countdown=60)  # Повторная попытка через 60 секунд
