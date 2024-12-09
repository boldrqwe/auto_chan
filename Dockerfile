# Используем официальный образ Python как базовый
FROM python:3.11-slim


# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Обновляем pip и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь код проекта в рабочую директорию
COPY . .

# Указываем команду по умолчанию (можно переопределить в docker-compose)
CMD ["python", "bot.py"]
