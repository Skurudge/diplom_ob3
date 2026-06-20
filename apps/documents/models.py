from typing import Any
from django.contrib.auth.models import User
from django.db import models


class Document(models.Model):
    """Модель для хранения и обработки загружаемых документов пользователей."""

    # Явно подсказываем PyCharm и mypy, что у модели будут эти динамические поля
    id: Any
    get_status_display: Any

    class Status(models.TextChoices):
        NEW = "NEW", "Новый"
        APPROVED = "APPROVED", "Одобрен"
        REJECTED = "REJECTED", "Отклонен"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Пользователь",
    )

    file = models.FileField(
        upload_to="documents/",
        verbose_name="Файл документа",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус верификации",
    )

    admin_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий администратора",
        help_text="Укажите причину отказа или важные заметки при проверке",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время загрузки",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего изменения",
    )

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Документ #{self.id} ({self.get_status_display()}) — {self.user.username}"
