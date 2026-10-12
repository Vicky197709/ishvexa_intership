from rest_framework import serializers
from .models import Event, Issue, Level


class EventSerializer(serializers.Serializer):
    project_key = serializers.CharField(max_length=64, write_only=True)
    message = serializers.CharField()
    stack_trace = serializers.CharField(required=False, allow_blank=True)
    level = serializers.ChoiceField(choices=Level.choices)
    environment = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()

    def validate_project_key(self, value):
        """Validate that the project key exists."""
        from apps.projects.models import Project
        if not Project.objects.filter(api_key=value).exists():
            raise serializers.ValidationError("Invalid project key")
        return value


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id', 'project', 'fingerprint', 'message', 'level',
            'environment', 'count', 'first_seen', 'last_seen', 'top_stack_frame'
        ]
        read_only_fields = ['id', 'fingerprint', 'count', 'first_seen', 'last_seen']


class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'message', 'stack_trace', 'level',
            'environment', 'timestamp', 'received_at'
        ]


class IssueDetailSerializer(serializers.ModelSerializer):
    recent_events = EventDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id', 'project', 'fingerprint', 'message', 'level',
            'environment', 'count', 'first_seen', 'last_seen',
            'top_stack_frame', 'recent_events'
        ]
        read_only_fields = ['id', 'fingerprint', 'count', 'first_seen', 'last_seen']
