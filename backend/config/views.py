"""
System-level API views for MediLocate AI.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

class HealthCheckView(APIView):
    """
    Liveness health check endpoint.
    Returns HTTP 200 with service identification when the application is operational.
    Does not expose sensitive system paths, credentials, or internal configuration.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "status": "ok",
                "service": "MediLocate API",
            },
            status=status.HTTP_200_OK,
        )
