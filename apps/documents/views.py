from typing import Any
from django.http import HttpRequest
from rest_framework import parsers, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.documents.models import Document
from apps.documents.serializers import DocumentSerializer, DocumentUploadSerializer
from apps.documents.tasks import send_admin_notification_task


@extend_schema_view(
    create=extend_schema(
        summary="Загрузка нового файла документа",
        description="Позволяет авторизованному пользователю загрузить файл документа.",
        request=DocumentUploadSerializer,
        responses={201: DocumentSerializer}
    )
)
class DocumentViewSet(viewsets.ModelViewSet):
    """API-эндпоинт для загрузки и просмотра документов зарегистрированными пользователями."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def get_queryset(self) -> Any:
        """Бизнес-логика: обычный пользователь видит только СВОИ загруженные документы.

        Защищено от ошибок генерации схем OpenAPI (Swagger).
        """
        # Безопасный пропуск для генератора схем drf-spectacular
        if getattr(self, "swagger_fake_view", False):
            return Document.objects.none()

        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Document.objects.all()
        return Document.objects.filter(user=user)

    def get_serializer_class(self) -> Any:
        """Динамический выбор сериализатора для валидации и вывода."""
        if self.action == "create":
            return DocumentUploadSerializer
        return DocumentSerializer

    def create(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """POST-запрос: Загрузка нового файла документа."""
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            document = Document.objects.create(
                user=request.user,
                file=serializer.validated_data["file"]
            )
            response_serializer = DocumentSerializer(document)

            # ИНТЕГРАЦИЯ CELERY: Отправляем задачу в фоновую очередь
            send_admin_notification_task.delay(document.id)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
