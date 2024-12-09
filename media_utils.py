# media_utils.py

import logging
import aiohttp
from telegram import InputMediaPhoto, InputMediaVideo

logger = logging.getLogger(__name__)

async def is_url_accessible(url: str) -> bool:
    """Проверяет доступность URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=10) as response:
                if response.status == 200:
                    return True
                else:
                    logger.warning(f"URL {url} вернул статус {response.status}")
                    return False
    except Exception as e:
        logger.warning(f"Ошибка при проверке URL {url}: {e}")
        return False

def create_input_media(url: str, caption: str = None):
    """Определяем тип медиа для отправки в группу."""
    logger.debug(f"Создание медиа-объекта для URL: {url}, caption: {caption is not None}")
    if any(url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
        return InputMediaPhoto(media=url, caption=caption, parse_mode='HTML')
    elif any(url.endswith(ext) for ext in [".webm", ".mp4"]):
        return InputMediaVideo(media=url, caption=caption, parse_mode='HTML')
    else:
        logger.debug("Неизвестный формат. Используем InputMediaPhoto по умолчанию.")
        return InputMediaPhoto(media=url, caption=caption, parse_mode='HTML')
