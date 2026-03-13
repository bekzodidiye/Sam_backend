from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, CheckIn, Sale, Message, Rule, MonthlyTarget, Tariff, DailyReport, SalesLink, Company

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('phone', 'nickname', 'first_name', 'last_name', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_superuser')
    
    # UserAdmin by default uses 'username'. We must override these completely.
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal info'), {'fields': ('nickname', 'first_name', 'last_name', 'email', 'avatar', 'role', 'league', 'achievements')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'nickname', 'password', 'first_name', 'last_name', 'email', 'role'),
        }),
    )
    
    search_fields = ('phone', 'first_name', 'last_name', 'email')
    ordering = ('phone',)

admin.site.register(CheckIn)
admin.site.register(Sale)
admin.site.register(Message)
admin.site.register(Rule)
admin.site.register(MonthlyTarget)
admin.site.register(Tariff)
admin.site.register(DailyReport)
admin.site.register(SalesLink)
admin.site.register(Company)
