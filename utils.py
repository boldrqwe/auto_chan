import httpx
import logging
from telegram import InputMediaPhoto, InputMediaVideo

logger = logging.getLogger(__name__)

async def is_url_accessible(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка проверки URL {url}: {e}")
        return False

def create_input_media(url: str, caption: str = None):
    if url.endswith((".jpg", ".jpeg", ".png", ".gif")):
        return InputMediaPhoto(media=url, caption=caption, parse_mode="HTML")
    elif url.endswith((".webm", ".mp4")):
        return InputMediaVideo(media=url, caption=caption, parse_mode="HTML")
    else:
        logger.warning(f"Неизвестный формат файла: {url}")
        return InputMediaPhoto(media=url, caption=caption, parse_mode="HTML")
