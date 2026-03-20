from rest_framework import viewsets, decorators
from rest_framework.response import Response
from django.db import models
from apps.models import Message
from ..serializers import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

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
