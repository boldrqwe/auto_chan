import logging
import asyncio
from media_utils import create_input_media

logger = logging.getLogger(__name__)

def job_collect_media(dvach, posted_media, media_queue):
    """Сбор медиа раз в минуту."""
    logger.info("Начинаем сбор медиа с Двача...")
    try:
        threads = dvach.fetch_threads(board="b")
        logger.info("Получено %d тредов.", len(threads))
    except Exception as e:
        logger.error(f"Не удалось получить треды: {e}")
        return

    threads_processed = 0
    media_found = 0

    for t in threads:
        thread_num = t.get("num") or t.get("thread_num")  # Проверяем поле num или thread_num
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

        # Разбиваем медиа на группы по 10 штук
        batch_size = 10
        media_groups = []
        for i in range(0, len(new_media), batch_size):
            batch = new_media[i:i+batch_size]
            # Формируем группу: первая группа, первый элемент - с подписью
            group = []
            for idx, u in enumerate(batch):
                if i == 0 and idx == 0:
                    # Первый элемент первой группы - с подписью
                    group.append(create_input_media(u, caption=t_data["caption"][:1024]))
                else:
                    group.append(create_input_media(u))
            media_groups.append(group)

        for g in media_groups:
            media_queue.append(g)
            media_found += len(g)

        threads_processed += 1
        logger.info("Тред %s обработан. Новых медиа: %d, групп: %d.", thread_num, len(new_media), len(media_groups))

    logger.info("Сбор медиа завершен. Обработано тредов: %d, найдено медиа: %d, очередь размером: %d",
                threads_processed, media_found, len(media_queue))

async def post_media_from_queue(bot, TELEGRAM_CHANNEL_ID, POST_INTERVAL, media_queue):
    """Отправка групп из очереди в канал."""
    logger.info("Запуск задачи отправки медиагрупп в Telegram.")
    while True:
        if media_queue:
            media_group = media_queue.pop(0)
            logger.info("Отправка медиагруппы из очереди: %s", [m.media for m in media_group])
            try:
                await bot.send_media_group(chat_id=TELEGRAM_CHANNEL_ID, media=media_group)
                logger.info("Медиагруппа успешно отправлена.")
                await asyncio.sleep(POST_INTERVAL)
            except Exception as e:
                logger.error(f"Ошибка при отправке медиагруппы: {e}")
        else:
            await asyncio.sleep(5)
