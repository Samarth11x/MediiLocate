"""
URL configuration for MediLocate AI backend project.
"""

from django.contrib import admin
from django.urls import path, include
from config.views import HealthCheckView, ChatMessageView

urlpatterns = [
    # Django Administration portal
    path('admin/', admin.site.urls),

    # Health check endpoint (Liveness probe)
    path('api/v1/health/', HealthCheckView.as_view(), name='api-health'),

    # MediBot conversational assistant endpoint
    path('api/v1/chat/', ChatMessageView.as_view(), name='api-chat'),

    # Medicine and pharmacy search endpoints
    path('api/v1/search/', include('apps.search.urls')),
]
