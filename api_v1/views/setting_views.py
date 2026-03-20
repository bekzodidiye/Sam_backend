from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.core.cache import cache
from apps.models import Rule, Tariff
from ..serializers import RuleSerializer, TariffSerializer
from .base import IsManager, broadcast_data_update

class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        cache_key = "system_rules_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 3600) # Cache for 1 hour
        return response

    def perform_create(self, serializer):
        serializer.save()
        cache.delete("system_rules_list")

    def perform_update(self, serializer):
        serializer.save()
        cache.delete("system_rules_list")

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete("system_rules_list")

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.select_related('company').all()
    serializer_class = TariffSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def list(self, request, *args, **kwargs):
        cache_key = "system_tariffs_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 3600)
        return response

    def perform_create(self, serializer):
        serializer.save()
        cache.delete("system_tariffs_list")

    def perform_update(self, serializer):
        serializer.save()
        cache.delete("system_tariffs_list")

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete("system_tariffs_list")

    @decorators.action(detail=False, methods=['post'], url_path='remove')
    def remove_tariff(self, request):
        company = request.data.get('company')
        name = request.data.get('tariff') or request.data.get('name')
        Tariff.objects.filter(company__name=company, name=name).delete()
        cache.delete("system_tariffs_list")
        return Response(status=status.HTTP_204_NO_CONTENT)
