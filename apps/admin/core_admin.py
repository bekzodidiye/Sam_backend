from django.contrib import admin
from ..models import Message, Rule

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__phone', 'recipient__phone', 'text')

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'created_at', 'updated_at')
