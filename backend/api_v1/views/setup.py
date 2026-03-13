from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from apps.models import Message, Rule, MonthlyTarget, Tariff, SalesLink
from ..serializers import (MessageSerializer, RuleSerializer, MonthlyTargetSerializer, 
                           TariffSerializer, SalesLinkSerializer)
from ..selectors import get_messages
from ..services import dispatch_message_notifications
from ..mixins import BroadcastMixin
from .users import IsManager

class MessageViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    broadcast_type = "NEW_MESSAGE"

    def get_queryset(self):
        return get_messages(self.request.user)

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        
        dispatch_message_notifications(
            sender=self.request.user, 
            recipient=message.recipient, 
            message_data=serializer.data
        )
        self.broadcast(None, data=serializer.data)

    @decorators.action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'read'})

class RuleViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    broadcast_type = "RULE_UPDATED"
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]

class MonthlyTargetViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = MonthlyTarget.objects.all()
    serializer_class = MonthlyTargetSerializer
    broadcast_type = "TARGET_UPDATED"

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def create(self, request, *args, **kwargs):
        month = request.data.get('month')
        instance = MonthlyTarget.objects.filter(month=month).first()
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return super().create(request, *args, **kwargs)

class TariffViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    broadcast_type = "TARIFF_UPDATED"

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    @decorators.action(detail=False, methods=['post'], url_path='remove')
    def remove_tariff(self, request):
        company = request.data.get('company')
        name = request.data.get('tariff') or request.data.get('name')
        Tariff.objects.filter(company__name=company, name=name).delete()
        self.broadcast(None)
        return Response(status=status.HTTP_204_NO_CONTENT)

class SalesLinkViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = SalesLink.objects.all()
    serializer_class = SalesLinkSerializer
    broadcast_type = "LINK_UPDATED"

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)
