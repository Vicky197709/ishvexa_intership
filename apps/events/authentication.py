from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from apps.projects.models import Project


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication using X-API-Key header.
    """
    
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return None
        
        try:
            project = Project.objects.get(api_key=api_key)
            return (None, project)  # Return None as user, project as auth
        except Project.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
