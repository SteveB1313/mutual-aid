from django.contrib import admin
from .models import Company, StormEvent, Deployment


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_name', 'phone', 'status', 'created_at']
    list_filter = ['status', 'services']
    search_fields = ['name', 'contact_name', 'email']


@admin.register(StormEvent)
class StormEventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'severity', 'created_at']
    list_filter = ['severity', 'date']
    search_fields = ['name', 'affected_area']


@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):
    list_display = ['company', 'storm_event', 'status', 'requested_at']
    list_filter = ['status', 'storm_event']
    search_fields = ['company__name', 'storm_event__name']
