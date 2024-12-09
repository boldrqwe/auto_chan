from telegram import InputMediaPhoto, InputMediaVideo

def create_input_media(url: str):
    """Определяем тип медиа для отправки в группу."""
    if any(url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
        return InputMediaPhoto(url)
    elif any(url.endswith(ext) for ext in [".webm", ".mp4"]):
        return InputMediaVideo(url)
    else:
        # По умолчанию считаем фото
        return InputMediaPhoto(url)
