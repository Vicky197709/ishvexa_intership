from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'api_key', 'created_at']
    search_fields = ['name', 'api_key']
    readonly_fields = ['id', 'created_at']
