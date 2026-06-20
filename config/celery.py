import os
from celery import Celery

# 1. Устанавливаем дефолтный модуль настроек Django для утилиты celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 2. Создаем экземпляр приложения Celery
app = Celery("diplom_ob3")

# 3. Загружаем настройки из файла settings.py с префиксом 'CELERY_'
app.config_from_object("django.conf:settings", namespace="CELERY")

# 4. Автоматически ищем фоновые задачи (tasks.py) во всех зарегистрированных приложениях Django
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Простая тестовая задача для проверки работоспособности Celery."""
    print(f"Request: {self.request!r}")
