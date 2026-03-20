from django.contrib import admin
from ..models import Sale, SalesLink, Company, Tariff

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'count', 'bonus', 'tariff', 'date')
    list_filter = ('date', 'company', 'user')
    search_fields = ('user__phone', 'user__first_name', 'user__last_name', 'company__name', 'tariff__name')

@admin.register(SalesLink)
class SalesLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'created_at')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'created_at')
    list_filter = ('company',)
