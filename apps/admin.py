from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, CheckIn, Sale, Message, Rule, MonthlyTarget, Tariff, DailyReport, SalesLink, Company

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'phone', 'first_name', 'last_name', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_superuser')
    
    # UserAdmin by default uses 'username'. We must override these completely.
    fieldsets = (
        (None, {'fields': ('username', 'phone', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'avatar', 'role', 'league', 'achievements')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'password', 'first_name', 'last_name', 'email', 'role'),
        }),
    )
    
    search_fields = ('username', 'phone', 'first_name', 'last_name', 'email')
    ordering = ('username',)

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'timestamp', 'check_out_time')
    list_filter = ('date', 'user')
    date_hierarchy = 'date'

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'count', 'bonus', 'tariff', 'date')
    list_filter = ('date', 'company', 'user')
    date_hierarchy = 'date'

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'timestamp')
    list_filter = ('date', 'user')
    date_hierarchy = 'date'

admin.site.register(Message)
admin.site.register(Rule)
admin.site.register(MonthlyTarget)
admin.site.register(Tariff)
admin.site.register(SalesLink)
admin.site.register(Company)
