from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.models import Message, Rule

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    senderName = serializers.CharField(source='sender.get_full_name', read_only=True)
    senderId = serializers.CharField(source='sender.id', read_only=True)
    recipientId = serializers.CharField(source='recipient.id', read_only=True, allow_null=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='recipient', write_only=True, required=False, allow_null=True
    )
    isRead = serializers.BooleanField(source='is_read', required=False)
    senderRole = serializers.CharField(source='sender.role', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'senderId', 'senderName', 'senderRole', 'recipientId', 'recipient_id', 'text', 'isRead', 'timestamp')
        read_only_fields = ('senderId', 'timestamp')

class RuleSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Rule
        fields = ('id', 'content', 'createdAt', 'updatedAt')
