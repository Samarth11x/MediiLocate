"""
Authentication and account management views for MediLocate AI.
Supports registration, login, logout, and authenticated session restoration.
"""

from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer, LoginSerializer, CurrentUserSerializer
from .models import AuditLog


def get_client_ip(request):
    """Safely extracts client IP address from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class RegisterView(APIView):
    """
    Public registration endpoint for Users and Pharmacists.
    Auto-authenticates session upon successful creation.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Establish Django session
            login(request, user)

            # Record audit event
            AuditLog.objects.create(
                actor=user,
                action='USER_REGISTERED',
                target_type='User',
                target_id=str(user.id),
                metadata={'role': user.profile.role, 'username': user.username},
                ip_address=get_client_ip(request),
            )

            return Response({
                'message': 'Registration successful.',
                'authenticated': True,
                'user': CurrentUserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)

        return Response({
            'message': 'Validation failed.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Authenticates existing users via username and password and starts a session.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)

            AuditLog.objects.create(
                actor=user,
                action='USER_LOGIN',
                target_type='User',
                target_id=str(user.id),
                metadata={'username': user.username},
                ip_address=get_client_ip(request),
            )

            return Response({
                'message': 'Login successful.',
                'authenticated': True,
                'user': CurrentUserSerializer(user).data,
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Authentication failed.',
            'authenticated': False,
            'errors': serializer.errors,
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Terminates the current user session.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        if request.user and request.user.is_authenticated:
            AuditLog.objects.create(
                actor=request.user,
                action='USER_LOGOUT',
                target_type='User',
                target_id=str(request.user.id),
                metadata={'username': request.user.username},
                ip_address=get_client_ip(request),
            )
        logout(request)
        return Response({
            'message': 'Logged out successfully.',
            'authenticated': False,
        }, status=status.HTTP_200_OK)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CurrentUserView(APIView):
    """
    Session restoration endpoint.
    Returns currently logged-in user details or authenticated: False if guest.
    Decorated with ensure_csrf_cookie so frontend receives a valid csrftoken cookie.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user and request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': CurrentUserSerializer(request.user).data,
            }, status=status.HTTP_200_OK)

        return Response({
            'authenticated': False,
            'user': None,
        }, status=status.HTTP_200_OK)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfTokenView(APIView):
    """
    Safe CSRF token bootstrap endpoint for single-page applications.
    Sets the csrftoken cookie and returns the token in the response payload.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        token = get_token(request)
        return Response({
            'csrfToken': token,
            'detail': 'CSRF cookie established successfully.'
        }, status=status.HTTP_200_OK)
