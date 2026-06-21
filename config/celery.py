import os
from celery import Celery

# 1. Устанавливаем дефолтный модуль настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 2. Создаем экземпляр приложения Celery
app = Celery("diplom_ob3")

# 3. Загружаем настройки из файла settings.py с префиксом 'CELERY_'
app.config_from_object("django.conf:settings", namespace="CELERY")

# 4. ИСПРАВЛЕНИЕ: Явно указываем путь к приложению для автопоиска задач
app.autodiscover_tasks(["apps.documents"])


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Тестовая задача для проверки Celery."""
    print(f"Request: {self.request!r}")
