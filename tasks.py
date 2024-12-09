import logging
import asyncio
from media_utils import create_input_media
from harkach_markup_converter import HarkachMarkupConverter

__STEP = 10  # Количество медиа в группе (максимум 10 для Telegram)

logger = logging.getLogger(__name__)

converter = HarkachMarkupConverter()

async def job_collect_media(dvach, posted_media, media_queue, batch_size=5, delay=10):
    """Сбор медиа с 2ch пакетами по batch_size тредов с паузой delay между пакетами."""
    logger.info("Начинаем сбор медиа с Двача...")

    try:
        threads = dvach.fetch_threads(board="b")  # Получение списка тредов
        logger.info("Получено %d тредов.", len(threads))
    except Exception as e:
        logger.error(f"Не удалось получить треды: {e}")
        return

    threads_processed = 0
    media_found = 0

    for i in range(0, len(threads), batch_size):
        batch = threads[i:i + batch_size]
        for t in batch:
            thread_num = t.get("num") or t.get("thread_num")
            if not thread_num:
                logger.debug(f"Пропускаем тред без номера: {t}")
                continue

            try:
                t_data = dvach.fetch_thread_data(thread_num, board="b")  # Данные треда
            except Exception as e:
                logger.error(f"Не удалось получить данные треда {thread_num}: {e}")
                continue

            if not t_data or not t_data["media"]:
                logger.debug(f"Тред {thread_num} не содержит медиа.")
                continue

            # Фильтруем новые медиа
            new_media = [m for m in t_data["media"] if m not in posted_media]
            if not new_media:
                logger.debug(f"Нет новых медиа в треде {thread_num}.")
                continue

            # Обновляем коллекцию отправленных медиа
            posted_media.update(new_media)

            # Преобразование разметки для подписи
            raw_caption = t_data["caption"][:1024]  # Ограничение Telegram на длину текста
            caption_html = converter.convert_to_tg_html(raw_caption)

            # Разбиваем медиа на группы
            media_groups = []
            for j in range(0, len(new_media), __STEP):
                group = [
                    create_input_media(url, caption=caption_html if j == 0 and idx == 0 else None)
                    for idx, url in enumerate(new_media[j:j + __STEP])
                ]
                media_groups.append(group)

            # Добавляем группы в очередь
            for g in media_groups:
                await media_queue.put(g)  # g — это список объектов InputMedia
                media_found += len(g)

            threads_processed += 1
            logger.info("Тред %s обработан. Новых медиа: %d, групп: %d.", thread_num, len(new_media), len(media_groups))

        # Пауза перед следующим пакетом
        logger.info("Пакет тредов обработан. Ждём %d секунд перед следующим пакетом.", delay)
        await asyncio.sleep(delay)

    logger.info("Сбор медиа завершен. Обработано тредов: %d, найдено медиа: %d, очередь размером: %d",
                threads_processed, media_found, media_queue.qsize())

    # Очистка коллекции отправленных медиа при необходимости
    if len(posted_media) > 10000:
        logger.info("Очистка коллекции отправленных медиа для уменьшения использования памяти.")
        posted_media.clear()

async def post_media_from_queue(bot, TELEGRAM_CHANNEL_ID, post_interval, media_queue):
    """Отправка медиагрупп из очереди в Telegram-канал."""
    logger.info("Запуск задачи отправки медиагрупп в Telegram.")
    while True:
        if not media_queue.empty():
            # Получаем медиагруппу из очереди
            media_group = await media_queue.get()
            logger.info("Отправка медиагруппы из очереди: %s", [m.media for m in media_group])

            try:
                # Отправляем медиагруппу
                await bot.send_media_group(chat_id=TELEGRAM_CHANNEL_ID, media=media_group)
                logger.info("Медиагруппа успешно отправлена.")
                await asyncio.sleep(post_interval)  # Пауза между отправками
            except Exception as e:
                logger.error(f"Ошибка при отправке медиагруппы: {e}")
                # Возвращаем группу обратно в очередь для повторной попытки
                await media_queue.put(media_group)
                await asyncio.sleep(post_interval)
        else:
            # Если очередь пуста, ждем 5 секунд перед повторной проверкой
            await asyncio.sleep(5)
