from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from api_v1.views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api_v1.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
