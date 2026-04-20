import os
from celery import Celery

# Установи переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('lms_project')

# Загрузи настройки из Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автообнаружение задач из всех установленных приложений
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')