from django.contrib import admin
from .models import Issue, Event


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'message', 'level', 'environment', 'count', 'first_seen', 'last_seen']
    list_filter = ['level', 'environment', 'created_at']
    search_fields = ['message', 'fingerprint']
    readonly_fields = ['id', 'fingerprint', 'count', 'first_seen', 'last_seen']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'issue', 'project', 'level', 'environment', 'timestamp', 'received_at']
    list_filter = ['level', 'environment', 'timestamp']
    search_fields = ['message']
    readonly_fields = ['id', 'received_at']
