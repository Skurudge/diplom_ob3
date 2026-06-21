# 1. Используем официальный стабильный образ Python 3.13 на базе Debian-slim
FROM python:3.13-slim

# 2. Настраиваем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Устанавливаем системные зависимости для работы компилятора и PostgreSQL (ИСПРАВЛЕНО)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# 5. Устанавливаем Poetry последней версии
RUN pip install --no-cache-dir poetry

# 6. Копируем файлы зависимостей проекта
COPY pyproject.toml poetry.lock /app/

# 7. Отключаем создание виртуального окружения Poetry внутри контейнера
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# 8. Копируем весь остальной код нашего дипломного проекта в контейнер
COPY . /app/

# 9. Открываем порт 8000 для Django
EXPOSE 8000
