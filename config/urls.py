from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from apps.documents.views import DocumentViewSet

# Настраиваем роутер для DRF API
router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")

urlpatterns = [
    # Панель администратора Django
    path("admin/", admin.site.urls),

    # Все эндпоинты приложения (доступны по адресу /api/v1/documents/)
    path("api/v1/", include(router.urls)),

    # Автогенерация схемы OpenAPI 3.0 от drf-spectacular
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Интерактивная документация Swagger UI для демонстрации на защите
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

# В режиме разработки разрешаем Django раздавать медиа-файлы (загруженные документы)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
