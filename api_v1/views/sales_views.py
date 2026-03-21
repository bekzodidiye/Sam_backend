from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from apps.models import Sale, SalesLink
from ..serializers import SaleSerializer, SalesLinkSerializer, UserSerializer
from .base import IsManager, broadcast_data_update, StandardResultsSetPagination

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(user=user)
        
        inventory = dict(user.inventory or {})
        company_name = instance.company.name
        total_to_remove = (instance.count or 0) + (instance.bonus or 0)
        
        current_amount = inventory.get(company_name, 0)
        inventory[company_name] = max(0, int(current_amount) - total_to_remove)
        
        user.inventory = inventory
        user.save()
        
        # Real-time updates
        broadcast_data_update("NEW_SALE", serializer.data)
        broadcast_data_update("USER_UPDATED", data=UserSerializer(user).data)

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_total = (old_instance.count or 0) + (old_instance.bonus or 0)
        old_company = old_instance.company.name
        
        instance = serializer.save()
        new_total = (instance.count or 0) + (instance.bonus or 0)
        new_company = instance.company.name
        
        user = instance.user
        inventory = dict(user.inventory or {})
        inventory[old_company] = int(inventory.get(old_company, 0)) + old_total
        inventory[new_company] = max(0, int(inventory.get(new_company, 0)) - new_total)
        
        user.inventory = inventory
        user.save()

        # Real-time updates
        broadcast_data_update("NEW_SALE", serializer.data)
        broadcast_data_update("USER_UPDATED", data=UserSerializer(user).data)

    def perform_destroy(self, instance):
        user = instance.user
        total_to_restore = (instance.count or 0) + (instance.bonus or 0)
        company_name = instance.company.name
        
        inventory = dict(user.inventory or {})
        inventory[company_name] = int(inventory.get(company_name, 0)) + total_to_restore
        
        user.inventory = inventory
        user.save()
        
        instance.delete()
        
        # Real-time updates
        broadcast_data_update("NEW_SALE", {"id": instance.id})
        broadcast_data_update("USER_UPDATED", data=UserSerializer(user).data)

    def get_queryset(self):
        return Sale.objects.select_related('user', 'company', 'tariff').only(
            'id', 'user__id', 'user__first_name', 'user__last_name', 
            'company__name', 'count', 'bonus', 'tariff__name', 'date', 'timestamp'
        ).all()

class SalesLinkViewSet(viewsets.ModelViewSet):
    queryset = SalesLink.objects.all()
    serializer_class = SalesLinkSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]










