from config.celery import app as celery_app

# Гарантируем, что приложение Celery загружается при старте Django
__all__ = ("celery_app",)
