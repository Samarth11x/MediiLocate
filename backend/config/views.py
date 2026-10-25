"""
System-level and conversational API views for MediLocate AI.
"""

import os
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

try:
    from services.medibot_service import get_medibot_dialogue_manager
except ImportError:
    from backend.services.medibot_service import get_medibot_dialogue_manager


class HealthCheckView(APIView):
    """
    Liveness and readiness health check endpoint for Render/container monitors.
    Returns HTTP 200 with service identification when the application is operational.
    Does not expose sensitive system paths, credentials, or internal configuration.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        is_healthy = True
        try:
            from django.db import connection
            connection.ensure_connection()
        except Exception:
            is_healthy = False

        if not is_healthy:
            return Response(
                {
                    "status": "degraded",
                    "service": "MediLocate API",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "status": "ok",
                "service": "MediLocate API",
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(ensure_csrf_cookie, name='dispatch')
class SpaFrontendView(View):
    """
    Single-Origin SPA View:
    Serves frontend/dist/index.html with the CSRF cookie securely attached
    so that frontend API requests have CSRF protection on first load.
    """
    def get(self, request, *args, **kwargs):
        index_file = settings.PROJECT_ROOT / 'frontend' / 'dist' / 'index.html'
        if index_file.exists():
            return FileResponse(open(index_file, 'rb'), content_type='text/html; charset=utf-8')
        return HttpResponse(
            """<!DOCTYPE html><html><head><title>MediLocate Backend</title></head>
            <body style="font-family:sans-serif;padding:40px;text-align:center;">
            <h2>MediLocate Backend API is Operational</h2>
            <p>API endpoints are active under <code>/api/v1/</code>.</p>
            <p>To enable Single-Origin UI delivery, run <code>npm run build</code> in <code>frontend/</code>.</p>
            </body></html>""",
            content_type='text/html; charset=utf-8',
            status=200,
        )


class ChatMessageView(APIView):
    """
    MediBot conversational assistant endpoint.

    Accepts user queries and context, routes to rule-based dialogue management
    with medical safety guardrails, and returns structured responses.
    Does not persist chat transcripts or sensitive health queries to the database.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, dict):
            return Response(
                {"error": "Request body must be a valid JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "message" not in request.data:
            return Response(
                {"error": "The 'message' field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_message = request.data.get("message")
        if not isinstance(raw_message, str):
            return Response(
                {"error": "The 'message' field must be a text string."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = raw_message.strip()
        if not message:
            return Response(
                {"error": "The 'message' field cannot be empty or whitespace only."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(message) > 500:
            return Response(
                {"error": "The 'message' field exceeds the maximum allowed length of 500 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        context = request.data.get("context")
        if context is not None and not isinstance(context, dict):
            return Response(
                {"error": "The 'context' field, if provided, must be a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            dialogue_manager = get_medibot_dialogue_manager()
            bot_response = dialogue_manager.process_message(
                user_message=message,
                context=context,
            )
            return Response(bot_response.to_dict(), status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {
                    "message": "An unexpected error occurred while processing your request. Please try again later.",
                    "intent": "UNKNOWN",
                    "status": "error",
                    "suggestions": ["Search for a medicine", "How does MediLocate work?"],
                    "results": [],
                    "demo_notice": False,
                    "safety_category": None,
                    "context": {},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
