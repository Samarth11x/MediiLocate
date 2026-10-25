"""
URL patterns for authentication endpoints in MediLocate AI.
"""

from django.urls import path
from .views import RegisterView, LoginView, LogoutView, CurrentUserView, CsrfTokenView

urlpatterns = [
    path('csrf/', CsrfTokenView.as_view(), name='auth-csrf'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', CurrentUserView.as_view(), name='auth-me'),
]
