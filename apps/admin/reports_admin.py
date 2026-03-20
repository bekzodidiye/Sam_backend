from django.contrib import admin
from ..models import MonthlyTarget, DailyReport

@admin.register(MonthlyTarget)
class MonthlyTargetAdmin(admin.ModelAdmin):
    list_display = ('month', 'targets')

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'timestamp')
    list_filter = ('date', 'user')
