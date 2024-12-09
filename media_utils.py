import logging
from telegram import InputMediaPhoto, InputMediaVideo

logger = logging.getLogger(__name__)

def create_input_media(url: str, caption: str = None):
    """Определяем тип медиа для отправки в группу, сразу задавая caption при создании."""
    logger.debug(f"Создание медиа-объекта для URL: {url}, caption: {'есть' if caption else 'нет'}")
    if any(url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
        return InputMediaPhoto(media=url, caption=caption)
    elif any(url.endswith(ext) for ext in [".webm", ".mp4"]):
        return InputMediaVideo(media=url, caption=caption)
    else:
        logger.debug("Неизвестный формат. Используем InputMediaPhoto по умолчанию.")
        return InputMediaPhoto(media=url, caption=caption)
