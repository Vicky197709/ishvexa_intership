import pytest
from django.test import RequestFactory
from rest_framework.exceptions import AuthenticationFailed
from apps.events.authentication import APIKeyAuthentication
from apps.projects.models import Project


@pytest.mark.django_db
class TestAPIKeyAuthentication:
    """Tests for API key authentication."""
    
    def test_valid_api_key(self):
        """Test authentication with valid API key."""
        project = Project.objects.create(name="Test Project", api_key="test-key-123")
        
        factory = RequestFactory()
        request = factory.get('/api/v1/issues/')
        request.META['HTTP_X_API_KEY'] = 'test-key-123'
        
        auth = APIKeyAuthentication()
        user, auth_project = auth.authenticate(request)
        
        assert user is None
        assert auth_project == project
    
    def test_missing_api_key(self):
        """Test authentication with missing API key."""
        factory = RequestFactory()
        request = factory.get('/api/v1/issues/')
        
        auth = APIKeyAuthentication()
        result = auth.authenticate(request)
        
        assert result is None
    
    def test_invalid_api_key(self):
        """Test authentication with invalid API key."""
        factory = RequestFactory()
        request = factory.get('/api/v1/issues/')
        request.META['HTTP_X_API_KEY'] = 'invalid-key'
        
        auth = APIKeyAuthentication()
        
        with pytest.raises(AuthenticationFailed) as exc_info:
            auth.authenticate(request)
        
        assert str(exc_info.value) == 'Invalid API key'
    
    def test_case_sensitive_api_key(self):
        """Test that API key is case sensitive."""
        Project.objects.create(name="Test Project", api_key="Test-Key-123")
        
        factory = RequestFactory()
        request = factory.get('/api/v1/issues/')
        request.META['HTTP_X_API_KEY'] = 'test-key-123'  # lowercase
        
        auth = APIKeyAuthentication()
        
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)
