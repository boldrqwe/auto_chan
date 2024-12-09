# auto_chan
# AutoChan

Бот для автоматического сбора медиа с 2ch и публикации их в Telegram-канал.

## Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/yourusername/auto_chan.git
    cd auto_chan
    ```

2. Создайте виртуальное окружение и активируйте его:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

4. Настройте переменные окружения:
    ```bash
    export BOT_TOKEN=your_telegram_bot_token
    export TELEGRAM_CHANNEL_ID=your_channel_id
    export TELEGRAM_POST_INTERVAL=50
    export FETCH_BATCH_SIZE=1
    export FETCH_DELAY=50
    ```

## Запуск

### Запуск бота

```bash
python bot.py
