from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, CheckIn, Sale, Message, Rule, MonthlyTarget, Tariff, DailyReport, SalesLink, Company

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username', 'phone', 'first_name', 'last_name', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_superuser')
    
    fieldsets = (
        (None, {'fields': ('username', 'phone', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'avatar', 'role', 'league', 'department', 'work_type', 'work_radius', 'work_location', 'achievements')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Extra Data'), {'fields': ('inventory', 'working_hours', 'league_history', 'plain_password')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'password', 'first_name', 'last_name', 'email', 'role'),
        }),
    )
    
    search_fields = ('username', 'phone', 'first_name', 'last_name', 'email')
    ordering = ('username', 'phone')

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'timestamp', 'check_out_time')
    list_filter = ('date', 'user')
    search_fields = ('user__phone', 'user__first_name', 'user__last_name')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'count', 'bonus', 'tariff', 'date')
    list_filter = ('date', 'company', 'user')
    search_fields = ('user__phone', 'user__first_name', 'user__last_name', 'company__name', 'tariff__name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__phone', 'recipient__phone', 'text')

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'created_at', 'updated_at')

@admin.register(MonthlyTarget)
class MonthlyTargetAdmin(admin.ModelAdmin):
    list_display = ('month', 'targets')

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'created_at')
    list_filter = ('company',)

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'timestamp')
    list_filter = ('date', 'user')

@admin.register(SalesLink)
class SalesLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'created_at')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)
