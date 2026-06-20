from typing import Any
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from apps.documents.models import Document
from apps.documents.tasks import send_user_status_notification_task


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Настройка панели администратора для управления документами пользователей."""

    list_display = (
        "id",
        "user",
        "status",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "user")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "id")
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

    actions = ["approve_documents", "reject_documents"]

    @admin.action(description="Одобрить выбранные документы")
    def approve_documents(self, request: HttpRequest, queryset: QuerySet[Document]) -> None:
        """Быстрое действие: Массовое одобрение документов с отправкой уведомлений."""
        # 1. Сначала массово обновляем статус в базе данных
        updated_count = queryset.update(status=Document.Status.APPROVED)

        # 2. ИНТЕГРАЦИЯ CELERY: Отправляем каждому пользователю фоновое письмо через очередь
        for document in queryset:
            send_user_status_notification_task.delay(document.id)

        self.message_user(
            request,
            f"Успешно одобрено документов: {updated_count}. Письма пользователям отправлены в очередь Celery.",
        )

    @admin.action(description="Отклонить выбранные документы")
    def reject_documents(self, request: HttpRequest, queryset: QuerySet[Document]) -> None:
        """Быстрое действие: Массовое отклонение документов с отправкой уведомлений."""
        # 1. Сначала массово обновляем статус в базе данных
        updated_count = queryset.update(status=Document.Status.REJECTED)

        # 2. ИНТЕГРАЦИЯ CELERY: Отправляем каждому пользователю фоновое письмо через очередь
        for document in queryset:
            send_user_status_notification_task.delay(document.id)

        self.message_user(
            request,
            f"Выбранные документы ({updated_count} шт.) были отклонены. Письма пользователям отправлены в очередь Celery.",
        )
