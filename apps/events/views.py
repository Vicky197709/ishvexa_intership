from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import Event, Issue
from .serializers import EventSerializer, IssueSerializer, IssueDetailSerializer
from .services import generate_fingerprint


@method_decorator(ratelimit(key='ip', rate='100/m', method='POST'), name='create')
class EventViewSet(viewsets.ViewSet):
    """
    ViewSet for handling error events.
    """
    
    @extend_schema(
        request=EventSerializer,
        responses={201: dict},
        description="Create a new error event"
    )
    def create(self, request):
        serializer = EventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        project_key = data['project_key']
        
        from apps.projects.models import Project
        project = Project.objects.get(api_key=project_key)
        
        # Generate fingerprint
        fingerprint = generate_fingerprint(data['message'], data.get('stack_trace', ''))
        
        # Extract top stack frame
        stack_trace = data.get('stack_trace', '')
        top_frame = ''
        if stack_trace:
            lines = stack_trace.strip().split('\n')
            top_frame = lines[0] if lines else ''
        
        # Try to find existing issue
        issue, created = Issue.objects.get_or_create(
            project=project,
            fingerprint=fingerprint,
            defaults={
                'message': data['message'],
                'level': data['level'],
                'environment': data['environment'],
                'first_seen': data['timestamp'],
                'last_seen': data['timestamp'],
                'top_stack_frame': top_frame,
            }
        )
        
        if not created:
            # Update existing issue
            issue.count += 1
            issue.last_seen = max(issue.last_seen, data['timestamp'])
            issue.save()
        
        # Create event
        Event.objects.create(
            issue=issue,
            project=project,
            message=data['message'],
            stack_trace=stack_trace,
            level=data['level'],
            environment=data['environment'],
            timestamp=data['timestamp'],
        )
        
        return Response({
            'issue_id': str(issue.id),
            'fingerprint': fingerprint,
            'created': created,
        }, status=status.HTTP_201_CREATED)


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving issues.
    """
    serializer_class = IssueSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        project = self.request.auth  # Project from authentication
        queryset = Issue.objects.filter(project=project)
        
        # Filters
        level = self.request.query_params.get('level')
        environment = self.request.query_params.get('environment')
        
        if level:
            queryset = queryset.filter(level=level)
        if environment:
            queryset = queryset.filter(environment=environment)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IssueDetailSerializer
        return IssueSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='level', type=OpenApiTypes.STR, description='Filter by level'),
            OpenApiParameter(name='environment', type=OpenApiTypes.STR, description='Filter by environment'),
            OpenApiParameter(name='page', type=OpenApiTypes.INT, description='Page number'),
            OpenApiParameter(name='page_size', type=OpenApiTypes.INT, description='Page size'),
        ],
        responses={200: IssueSerializer},
        description="List issues with pagination and filters"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        responses={200: IssueDetailSerializer},
        description="Get issue details with recent events"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Get recent events (last 10)
        recent_events = instance.events.all()[:10]
        data = serializer.data
        data['recent_events'] = EventDetailSerializer(recent_events, many=True).data
        
        return Response(data)
