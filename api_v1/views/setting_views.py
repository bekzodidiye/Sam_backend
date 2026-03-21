from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.translation import get_language
from apps.models import Rule, Tariff, GlobalSetting
from ..serializers import RuleSerializer, TariffSerializer
from .base import IsManager, broadcast_data_update

class GlobalSettingsViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == 'create':
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    def list(self, request):
        settings = GlobalSetting.get_settings()
        return Response({
            "id": settings.id,
            "rating_enabled": settings.rating_enabled,
            "updated_at": settings.updated_at
        })

    def create(self, request):
        settings = GlobalSetting.get_settings()
        if 'rating_enabled' in request.data:
            settings.rating_enabled = request.data['rating_enabled']
        settings.last_modified_by = request.user
        settings.save()
        
        # Invalidate cache if there's any settings cache
        cache.delete("global_settings")
        
        broadcast_data_update("SETTINGS_UPDATED", {
            "id": settings.id,
            "rating_enabled": settings.rating_enabled,
            "updated_at": settings.updated_at.isoformat() if settings.updated_at else None
        })
        
        return Response({
            "id": settings.id,
            "rating_enabled": settings.rating_enabled,
            "updated_at": settings.updated_at
        })

class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        lang = get_language()
        cache_key = f"system_rules_list_{lang}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 3600) # Cache for 1 hour
        return response

    def _clear_cache(self):
        for lang, _ in [('uz', 'Uzbek'), ('ru', 'Russian'), ('en', 'English')]:
            cache.delete(f"system_rules_list_{lang}")

    def perform_create(self, serializer):
        serializer.save()
        self._clear_cache()

    def perform_update(self, serializer):
        serializer.save()
        self._clear_cache()

    def perform_destroy(self, instance):
        instance.delete()
        self._clear_cache()

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.select_related('company').all()
    serializer_class = TariffSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def list(self, request, *args, **kwargs):
        lang = get_language()
        cache_key = f"system_tariffs_list_{lang}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 3600)
        return response

    def _clear_cache(self):
        for lang, _ in [('uz', 'Uzbek'), ('ru', 'Russian'), ('en', 'English')]:
            cache.delete(f"system_tariffs_list_{lang}")

    def perform_create(self, serializer):
        serializer.save()
        self._clear_cache()

    def perform_update(self, serializer):
        serializer.save()
        self._clear_cache()

    def perform_destroy(self, instance):
        instance.delete()
        self._clear_cache()

    @decorators.action(detail=False, methods=['post'], url_path='remove')
    def remove_tariff(self, request):
        company = request.data.get('company')
        name = request.data.get('tariff') or request.data.get('name')
        Tariff.objects.filter(company__name=company, name=name).delete()
        cache.delete("system_tariffs_list")
        return Response(status=status.HTTP_204_NO_CONTENT)
