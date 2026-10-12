import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from apps.projects.models import Project
from apps.events.models import Issue, Event, Level


@pytest.mark.django_db
class TestEventViewSet:
    """Tests for Event creation endpoint."""
    
    def setup_method(self):
        self.client = APIClient()
        self.project = Project.objects.create(name="Test Project", api_key="test-key-123")
    
    def test_create_event_success(self):
        """Test successful event creation."""
        payload = {
            "project_key": "test-key-123",
            "message": "Test error",
            "stack_trace": "File test.py, line 10",
            "level": "error",
            "environment": "production",
            "timestamp": timezone.now().isoformat()
        }
        
        response = self.client.post('/api/v1/events/', payload, format='json')
        
        assert response.status_code == 201
        assert 'issue_id' in response.data
        assert 'fingerprint' in response.data
        assert response.data['created'] is True
        
        # Verify issue was created
        assert Issue.objects.count() == 1
        assert Event.objects.count() == 1
    
    def test_create_event_groups_duplicates(self):
        """Test that duplicate events are grouped into same issue."""
        payload = {
            "project_key": "test-key-123",
            "message": "Test error",
            "stack_trace": "File test.py, line 10",
            "level": "error",
            "environment": "production",
            "timestamp": timezone.now().isoformat()
        }
        
        # Create first event
        response1 = self.client.post('/api/v1/events/', payload, format='json')
        issue_id_1 = response1.data['issue_id']
        
        # Create duplicate event
        response2 = self.client.post('/api/v1/events/', payload, format='json')
        issue_id_2 = response2.data['issue_id']
        
        assert response1.data['created'] is True
        assert response2.data['created'] is False
        assert issue_id_1 == issue_id_2
        
        # Verify issue count increased
        issue = Issue.objects.get(id=issue_id_1)
        assert issue.count == 2
        assert Event.objects.count() == 2
    
    def test_create_event_invalid_project_key(self):
        """Test event creation with invalid project key."""
        payload = {
            "project_key": "invalid-key",
            "message": "Test error",
            "level": "error",
            "environment": "production",
            "timestamp": timezone.now().isoformat()
        }
        
        response = self.client.post('/api/v1/events/', payload, format='json')
        
        assert response.status_code == 400
        assert 'project_key' in response.data
    
    def test_create_event_missing_required_fields(self):
        """Test event creation with missing required fields."""
        payload = {
            "project_key": "test-key-123",
            "message": "Test error"
        }
        
        response = self.client.post('/api/v1/events/', payload, format='json')
        
        assert response.status_code == 400


@pytest.mark.django_db
class TestIssueViewSet:
    """Tests for Issue listing and retrieval."""
    
    def setup_method(self):
        self.client = APIClient()
        self.project = Project.objects.create(name="Test Project", api_key="test-key-123")
        self.client.credentials(HTTP_X_API_KEY='test-key-123')
    
    def test_list_issues_requires_auth(self):
        """Test that listing issues requires authentication."""
        self.client.credentials()  # Remove credentials
        response = self.client.get('/api/v1/issues/')

        assert response.status_code == 403
    
    def test_list_issues_success(self):
        """Test successful issue listing."""
        # Create some issues
        issue1 = Issue.objects.create(
            project=self.project,
            fingerprint="fp1",
            message="Error 1",
            level="error",
            environment="production",
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        issue2 = Issue.objects.create(
            project=self.project,
            fingerprint="fp2",
            message="Error 2",
            level="warning",
            environment="staging",
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        response = self.client.get('/api/v1/issues/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 2
    
    def test_list_issues_filter_by_level(self):
        """Test filtering issues by level."""
        Issue.objects.create(
            project=self.project,
            fingerprint="fp1",
            message="Error 1",
            level="error",
            environment="production",
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        Issue.objects.create(
            project=self.project,
            fingerprint="fp2",
            message="Error 2",
            level="warning",
            environment="production",
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        response = self.client.get('/api/v1/issues/?level=error')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['level'] == 'error'
    
    def test_list_issues_filter_by_environment(self):
        """Test filtering issues by environment."""
        Issue.objects.create(
            project=self.project,
            fingerprint="fp1",
            message="Error 1",
            level="error",
            environment="production",
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        Issue.objects.create(
            project=self.project,
            fingerprint="fp2",
            message="Error 2",
            level="error",
            environment="staging",
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        response = self.client.get('/api/v1/issues/?environment=production')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['environment'] == 'production'
    
    def test_retrieve_issue_details(self):
        """Test retrieving issue details with recent events."""
        issue = Issue.objects.create(
            project=self.project,
            fingerprint="fp1",
            message="Error 1",
            level="error",
            environment="production",
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        # Create some events
        for i in range(5):
            Event.objects.create(
                issue=issue,
                project=self.project,
                message="Error 1",
                stack_trace=f"Frame {i}",
                level="error",
                environment="production",
                timestamp=timezone.now()
            )
        
        response = self.client.get(f'/api/v1/issues/{issue.id}/')
        
        assert response.status_code == 200
        assert response.data['id'] == str(issue.id)
        assert 'recent_events' in response.data
        assert len(response.data['recent_events']) == 5
    
    def test_retrieve_issue_from_other_project(self):
        """Test that users cannot access issues from other projects."""
        other_project = Project.objects.create(name="Other Project", api_key="other-key")
        other_issue = Issue.objects.create(
            project=other_project,
            fingerprint="fp1",
            message="Error 1",
            level="error",
            environment="production",
            first_seen=timezone.now(),
            last_seen=timezone.now()
        )
        
        response = self.client.get(f'/api/v1/issues/{other_issue.id}/')
        
        assert response.status_code == 404
