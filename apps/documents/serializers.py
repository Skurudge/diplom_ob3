from typing import Any
from rest_framework import serializers
from apps.documents.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о документах."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "username",
            "file",
            "status",
            "status_display",
            "admin_comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "admin_comment", "created_at", "updated_at")


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Сериализатор, который отвечает строго за валидацию загружаемого файла."""

    # Явно указываем тип поля для корректного отображения кнопки в Swagger UI
    file = serializers.FileField(required=True, label="Файл документа")

    class Meta:
        model = Document
        fields = ("file",)

    def validate_file(self, value: Any) -> Any:
        """Бизнес-валидация: проверка расширения и размера файла."""
        max_size = 10 * 1024 * 1024  # 10 МБ в байтах
        if value.size > max_size:
            raise serializers.ValidationError("Размер файла не должен превышать 10 МБ.")

        ext = value.name.split(".")[-1].lower()
        valid_extensions = ["pdf", "jpg", "jpeg", "png", "doc", "docx"]
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Неподдерживаемый формат файла. Разрешены только: {', '.join(valid_extensions)}"
            )

        return value
