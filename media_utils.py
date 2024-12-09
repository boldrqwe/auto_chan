import logging
from telegram import InputMediaPhoto, InputMediaVideo

logger = logging.getLogger(__name__)

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
