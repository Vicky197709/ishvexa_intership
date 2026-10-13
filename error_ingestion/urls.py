from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

# Create views without authentication
@authentication_classes([])
@permission_classes([AllowAny])
class SchemaView(SpectacularAPIView):
    pass

@authentication_classes([])
@permission_classes([AllowAny])
class SwaggerView(SpectacularSwaggerView):
    pass

@authentication_classes([])
@permission_classes([AllowAny])
class RedocView(SpectacularRedocView):
    pass

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SchemaView.as_view(), name='schema'),
    path('api/docs/', SwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', RedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/', include('apps.events.urls')),
]
