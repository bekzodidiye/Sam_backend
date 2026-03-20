from django.contrib import admin
from ..models import CheckIn

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'timestamp', 'check_out_time')
    list_filter = ('date', 'user')
    search_fields = ('user__phone', 'user__first_name', 'user__last_name')
