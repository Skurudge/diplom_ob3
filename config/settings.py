import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Загрузка переменных окружения
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# 2. Основные настройки безопасности
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-fallback-key")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

allowed_hosts_raw = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_raw.split(",")]

# 3. Определение установленных приложений
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонние библиотеки
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
    # Локальные приложения диплома
    "apps.documents",
]

# 4. Промежуточное ПО (Middleware)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# 5. Шаблоны
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 6. Подключение к базе данных PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "ob3_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# 7. Валидация паролей пользователей
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# 8. Язык и время
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# 9. Статические и Медиа-файлы
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 10. Настройки Django Rest Framework (DRF)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "OB3 Document Processing API",
    "DESCRIPTION": "Дипломный проект: Сервис обработки загружаемых документов",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# 11. Настройки очередей Celery и Redis
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# 12. РЕЖИМ РАЗРАБОТКИ: Письма отправляются прямо в консоль терминала
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@platform.com")
