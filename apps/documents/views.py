from typing import Any
from django.http import HttpRequest
from rest_framework import parsers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.documents.models import Document
from apps.documents.serializers import DocumentSerializer, DocumentUploadSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """API-эндпоинт для загрузки и просмотра документов зарегистрированными пользователями."""

    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def get_queryset(self) -> Any:
        """Бизнес-логика: обычный пользователь видит только СВОИ загруженные документы.

        Администратор видит абсолютно все документы в системе.
        """
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

            # ПРИМЕЧАНИЕ: Сюда мы добавим вызов задачи Celery для уведомления админа!
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
