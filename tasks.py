# tasks.py
import logging
import asyncio
from media_utils import create_input_media
from harkach_markup_converter import HarkachMarkupConverter

__STEP = 6

logger = logging.getLogger(__name__)

converter = HarkachMarkupConverter()

async def job_collect_media(dvach, posted_media, media_queue, batch_size=5, delay=10):
    """Сбор медиа с 2ch пакетами по batch_size тредов с паузой delay между пакетами."""
    logger.info("Начинаем сбор медиа с Двача...")

    try:
        threads = dvach.fetch_threads(board="b")
        logger.info("Получено %d тредов.", len(threads))
    except Exception as e:
        logger.error(f"Не удалось получить треды: {e}")
        return

    threads_processed = 0
    media_found = 0

    # Разделяем список тредов на пакеты
    for i in range(0, len(threads), batch_size):
        batch = threads[i:i + batch_size]
        for t in batch:
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

            # Фильтруем уже отправленные медиа
            new_media = [m for m in t_data["media"] if m not in posted_media]
            if not new_media:
                logger.debug("Нет новых медиа в треде %s.", thread_num)
                continue

            # Добавляем новые медиа в posted_media
            for m_url in new_media:
                posted_media.add(m_url)

            # Преобразуем разметку для caption
            raw_caption = t_data["caption"][:1024]
            caption_html = converter.convert_to_tg_html(raw_caption)

            # Разбиваем медиа на группы по 10 штук
            media_groups = []
            for j in range(0, len(new_media), __STEP):
                group = []
                batch_group = new_media[j:j + __STEP]
                for idx, u in enumerate(batch_group):
                    # Первый элемент первой группы с подписью
                    if j == 0 and idx == 0:
                        group.append(create_input_media(u, caption=caption_html))
                    else:
                        group.append(create_input_media(u))
                media_groups.append(group)

            # Добавляем группы в очередь на отправку
            for g in media_groups:
                await media_queue.put(g)
                media_found += len(g)

            threads_processed += 1
            logger.info("Тред %s обработан. Новых медиа: %d, групп: %d.", thread_num, len(new_media), len(media_groups))

        # Пауза перед следующим пакетом тредов
        logger.info("Пакет тредов обработан. Ждём %d секунд перед следующим пакетом.", delay)
        await asyncio.sleep(delay)

    logger.info("Сбор медиа завершен. Обработано тредов: %d, найдено медиа: %d, очередь размером: %d",
                threads_processed, media_found, media_queue.qsize())

    # Очистка posted_media для уменьшения потребления памяти
    if len(posted_media) > 10000:
        logger.info("Очистка коллекции отправленных медиа.")
        posted_media.clear()

async def post_media_from_queue(bot, TELEGRAM_CHANNEL_ID, post_interval, media_queue):
    """Отправка групп из очереди в Telegram-канал."""
    logger.info("Запуск задачи отправки медиагрупп в Telegram.")
    while True:
        if not media_queue.empty():
            media_group = await media_queue.get()
            logger.info("Отправка медиагруппы из очереди: %s", [m.media for m in media_group])
            try:
                await bot.send_media_group(chat_id=TELEGRAM_CHANNEL_ID, media=media_group, parse_mode='HTML')
                logger.info("Медиагруппа успешно отправлена.")
                await asyncio.sleep(post_interval)  # Пауза между отправками
            except Exception as e:
                logger.error(f"Ошибка при отправке медиагруппы: {e}")
                # Если произошла ошибка, вернём группу обратно в очередь для повторной попытки
                await media_queue.put(media_group)
                await asyncio.sleep(post_interval)
        else:
            # Если очередь пуста, ждём 5 секунд перед повторной проверкой
            await asyncio.sleep(5)
