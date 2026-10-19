"""
URL configuration for MediLocate AI backend project.
"""

from django.contrib import admin
from django.urls import path
from config.views import HealthCheckView

urlpatterns = [
    # Django Administration portal
    path('admin/', admin.site.urls),

    # Health check endpoint (Liveness probe)
    path('api/v1/health/', HealthCheckView.as_view(), name='api-health'),
]
