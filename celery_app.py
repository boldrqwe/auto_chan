# celery_app.py

from celery import Celery

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Автоматическое обнаружение задач в пакете tasks
app.autodiscover_tasks(['tasks'])

# Настройка периодических задач
app.conf.beat_schedule = {
    'collect-media-every-minute': {
        'task': 'tasks.collect_media_task',
        'schedule': 60.0,  # каждые 60 секунд
    },
    'post-media-every-30-seconds': {
        'task': 'tasks.post_media_task',
        'schedule': 30.0,  # каждые 30 секунд
    },
}
app.conf.timezone = 'UTC'
