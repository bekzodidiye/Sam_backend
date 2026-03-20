from rest_framework import viewsets, decorators
from rest_framework.response import Response
from django.db import models
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.models import Message
from ..serializers import MessageSerializer
from .base import broadcast_data_update

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        channel_layer = get_channel_layer()
        notification_data = {
            "type": "send_notification",
            "message": {
                "type": "NEW_MESSAGE",
                "data": serializer.data
            }
        }
        
        if message.recipient:
            async_to_sync(channel_layer.group_send)(
                f"user_{message.recipient.id}",
                notification_data
            )
        else:
            if self.request.user.role == 'manager':
                async_to_sync(channel_layer.group_send)("everyone", notification_data)
            else:
                async_to_sync(channel_layer.group_send)("managers", notification_data)
        
        broadcast_data_update("NEW_MESSAGE", data=serializer.data)

    def get_queryset(self):
        user = self.request.user
        qs = Message.objects.select_related('sender', 'recipient')
        if user.role == 'manager':
            return qs.filter(
                models.Q(recipient=user) | 
                models.Q(recipient__isnull=True) | 
                models.Q(sender=user)
            )
        else:
            return qs.filter(
                models.Q(recipient=user) | 
                models.Q(sender=user) |
                models.Q(recipient__isnull=True, sender__role='manager')
            )

    @decorators.action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'read'})
