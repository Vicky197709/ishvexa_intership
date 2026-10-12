import uuid
import hashlib
from django.db import models
from django.utils import timezone


class Level(models.TextChoices):
    ERROR = 'error', 'Error'
    WARNING = 'warning', 'Warning'
    INFO = 'info', 'Info'


class Issue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='issues')
    fingerprint = models.CharField(max_length=64, unique=True, db_index=True)
    message = models.TextField()
    level = models.CharField(max_length=10, choices=Level.choices, db_index=True)
    environment = models.CharField(max_length=50, db_index=True)
    count = models.PositiveIntegerField(default=1)
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    top_stack_frame = models.TextField(blank=True)

    class Meta:
        db_table = 'issues'
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['project', 'level']),
            models.Index(fields=['project', 'environment']),
        ]

    def __str__(self):
        return f"{self.message[:50]}... ({self.count} occurrences)"


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='events')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='events')
    message = models.TextField()
    stack_trace = models.TextField(blank=True)
    level = models.CharField(max_length=10, choices=Level.choices)
    environment = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['issue', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.level}: {self.message[:50]}..."
