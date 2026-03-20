from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from ..models import User

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
