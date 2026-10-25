"""
URL configuration for MediLocate AI backend project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from config.views import HealthCheckView, ChatMessageView, SpaFrontendView

urlpatterns = [
    # React Admin Portal route (must precede Django admin to prevent 404 on /admin/dashboard)
    re_path(r'^admin/dashboard(?:/.*)?$', SpaFrontendView.as_view(), name='admin-dashboard-spa'),

    # Django Administration portal
    path('admin/', admin.site.urls),

    # Health check endpoint (Liveness probe for Render)
    path('api/v1/health/', HealthCheckView.as_view(), name='api-health'),

    # MediBot conversational assistant endpoint
    path('api/v1/chat/', ChatMessageView.as_view(), name='api-chat'),

    # Medicine and pharmacy search endpoints
    path('api/v1/search/', include('apps.search.urls')),

    # Authentication & User Account endpoints
    path('api/v1/auth/', include('apps.accounts.urls')),

    # Pharmacist Portal endpoints
    path('api/v1/pharmacist/', include('apps.pharmacies.pharmacist_urls')),

    # Admin Portal endpoints
    path('api/v1/admin/', include('apps.accounts.admin_urls')),

    # Single-Origin SPA Frontend route (serves Vite React application for all client paths)
    re_path(r'^(?!api/|admin/|static/).*$', SpaFrontendView.as_view(), name='spa-frontend'),
]
