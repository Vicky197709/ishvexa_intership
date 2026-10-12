from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, IssueViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'issues', IssueViewSet, basename='issue')

urlpatterns = [
    path('', include(router.urls)),
]
