from typing import Any
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.documents.models import Document


class DummyStorage:
    """Легковесный класс-заглушка для тестирования сообщений в Django Admin без MIDDLEWARE."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.messages: list[str] = []

    def add(self, level: int, message: str, extra_tags: str = "") -> None:
        self.messages.append(message)


class DocumentAPITestCase(TestCase):
    """Комплексные тесты для проверки безопасности, валидации и бизнес-логики сервиса документов."""

    def setUp(self) -> None:
        # Инициализируем тестовый клиент DRF
        self.client = APIClient()
        # Фабрика запросов для тестирования админки
        self.factory = RequestFactory()

        # Создаем обычного тестового пользователя
        self.user = User.objects.create_user(username="testuser", password="password123", email="user@test.com")

        # Создаем пользователя-администратора
        self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpassword123")

        # Ссылка на эндпоинт загрузки и просмотра документов
        self.url = reverse("document-list")

    def test_upload_document_unauthorized(self) -> None:
        """Безопасность: Анонимный пользователь не может загрузить документ."""
        fake_file = SimpleUploadedFile("passport.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(self.url, {"file": fake_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_valid_document_success(self) -> None:
        """Бизнес-логика: Зарегистрированный пользователь может успешно загрузить валидный PDF."""
        self.client.force_authenticate(user=self.user)

        valid_file = SimpleUploadedFile("case1_pasport.pdf", b"dummy pdf data", content_type="application/pdf")
        response = self.client.post(self.url, {"file": valid_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

        document = Document.objects.first()
        self.assertIsNotNone(document)
        if document:
            self.assertEqual(document.user, self.user)
            self.assertEqual(document.status, Document.Status.NEW)

    def test_upload_invalid_file_extension(self) -> None:
        """Валидация: Система блокирует файлы с неподдерживаемым расширением."""
        self.client.force_authenticate(user=self.user)

        invalid_file = SimpleUploadedFile("virus.exe", b"dangerous code", content_type="application/x-msdownload")
        response = self.client.post(self.url, {"file": invalid_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    def test_user_sees_only_own_documents(self) -> None:
        """Изоляция данных: Пользователь видит в списке только свои документы."""
        other_user = User.objects.create_user(username="otheruser", password="password")
        fake_file = SimpleUploadedFile("other_doc.pdf", b"data", content_type="application/pdf")
        Document.objects.create(user=other_user, file=fake_file)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_admin_action_approve_and_reject(self) -> None:
        """Модерация: Администратор может массово одобрять или отклонять документы."""
        fake_file = SimpleUploadedFile("doc.pdf", b"data", content_type="application/pdf")
        document = Document.objects.create(user=self.user, file=fake_file)

        self.assertEqual(document.status, Document.Status.NEW)

        from django.contrib.admin.sites import AdminSite
        from apps.documents.admin import DocumentAdmin

        site = AdminSite()
        model_admin = DocumentAdmin(Document, site)
        queryset = Document.objects.filter(id=document.id)

        # Создаем фейковый HTTP-запрос для прохождения message_user
        request = self.factory.get("/admin/documents/document/")
        request.user = self.admin_user

        # Подключаем нашу безопасную заглушку сообщений
        setattr(request, "_messages", DummyStorage())

        # 1. Проверяем действие "Одобрить"
        model_admin.approve_documents(request=request, queryset=queryset)
        document.refresh_from_db()
        self.assertEqual(document.status, Document.Status.APPROVED)

        # 2. Проверяем действие "Отклонить"
        model_admin.reject_documents(request=request, queryset=queryset)
        document.refresh_from_db()
        self.assertEqual(document.status, Document.Status.REJECTED)
