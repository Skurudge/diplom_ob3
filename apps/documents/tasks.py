from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from apps.documents.models import Document


@shared_task
def send_admin_notification_task(document_id: int) -> str:
    """Фоновая задача Celery: Уведомление администратора о новом документе."""
    try:
        document = Document.objects.get(id=document_id)
        subject = f"🔥 Новый документ на проверку #{document.id}"
        message = (
            f"Пользователь {document.user.username} загрузил новый документ.\n"
            f"Имя файла: {document.file.name}\n"
            f"Пожалуйста, проверьте его в панели администратора Django."
        )

        # Отправляем письмо (оно напечатается в консоли воркера Celery)
        send_mail(
            subject=subject,
            message=message,
            from_email=(
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, "DEFAULT_FROM_EMAIL") else "noreply@platform.com"
            ),
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        return f"Успешно отправлено уведомление админу по документу #{document_id}"
    except Document.DoesNotExist:
        return f"Ошибка: Документ #{document_id} не найден"


@shared_task
def send_user_status_notification_task(document_id: int) -> str:
    """Фоновая задача Celery: Уведомление пользователя об изменении статуса его документа."""
    try:
        document = Document.objects.get(id=document_id)
        status_label = document.get_status_display()

        subject = f"📋 Статус вашего документа #{document.id} обновлен"
        message = (
            f"Здравствуйте, {document.user.username}!\n\n"
            f'Статус верификации вашего документа был изменен на: "{status_label}".\n'
        )

        # Если администратор оставил текстовый комментарий (например, причину отказа)
        if document.admin_comment:
            message += f"Комментарий проверяющего: {document.admin_comment}\n"

        message += "\nС уважением, Команда платформы."

        send_mail(
            subject=subject,
            message=message,
            from_email="noreply@platform.com",
            recipient_list=[document.user.email if document.user.email else "user@example.com"],
            fail_silently=False,
        )
        return f"Успешно отправлено уведомление пользователю по документу #{document_id}"
    except Document.DoesNotExist:
        return f"Ошибка: Документ #{document_id} не найден"
