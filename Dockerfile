# Пример, если Redis не в контейнере, а Managed service Railway:
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV BOT_TOKEN=${BOT_TOKEN}
ENV TELEGRAM_CHANNEL_ID=${TELEGRAM_CHANNEL_ID}
ENV TELEGRAM_POST_INTERVAL=10

# Предположим, Railway даёт REDIS_URL, который вы поставите в Variables проекта
# Не запускаем локальный redis-server, так как используется внешний Redis.

RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

RUN echo "[supervisord]\nnodaemon=true\n\n[program:celery-worker]\ncommand=celery -A tasks worker --loglevel=INFO\n\n[program:celery-beat]\ncommand=celery -A tasks beat --loglevel=INFO\n\n[program:web]\ncommand=python bot.py" > /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

