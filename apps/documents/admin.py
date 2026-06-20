from typing import Any
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from apps.documents.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Настройка панели администратора для управления документами пользователей."""

    # 1. Какие поля отображать в виде таблицы в списке документов
    list_display = (
        "id",
        "user",
        "status",
        "created_at",
        "updated_at",
    )

    # 2. Поля, на которые можно кликнуть, чтобы перейти внутрь документа
    list_display_links = ("id", "user")

    # 3. Фильтры в правой панели для быстрой сортировки документов администратором
    list_filter = ("status", "created_at")

    # 4. Поля для поиска (по имени пользователя, его email или ID документа)
    search_fields = ("user__username", "user__email", "id")

    # 5. Настройка полей внутри самого документа при детальном просмотре
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": ("user", "file", "status"),
            },
        ),
        (
            "Модерация",
            {
                "fields": ("admin_comment",),
            },
        ),
        (
            "Системные даты",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    # 6. БЫСТРЫЕ ДЕЙСТВИЯ (Actions) — требование из ТЗ
    actions = ["approve_documents", "reject_documents"]

    @admin.action(description="Одобрить выбранные документы")
    def approve_documents(self, request: HttpRequest, queryset: QuerySet[Document]) -> None:
        """Быстрое действие: Массовое одобрение документов."""
        # Обновляем статус в базе данных
        updated_count = queryset.update(status=Document.Status.APPROVED)

        # Выводим красивое системное уведомление вверху экрана для админа
        self.message_user(
            request,
            f"Успешно одобрено документов: {updated_count}.",
        )

        # ПРИМЕЧАНИЕ: Сюда мы завтра добавим вызов задачи Celery для отправки писем пользователям!

    @admin.action(description="Отклонить выбранные документы")
    def reject_documents(self, request: HttpRequest, queryset: QuerySet[Document]) -> None:
        """Быстрое действие: Массовое отклонение документов."""
        # Обновляем статус в базе данных
        updated_count = queryset.update(status=Document.Status.REJECTED)

        # Выводим уведомление для админа
        self.message_user(
            request,
            f"Выбранные документы ({updated_count} шт.) были отклонены.",
        )

        # ПРИМЕЧАНИЕ: Сюда мы завтра добавим вызов задачи Celery для отправки писем пользователям!
