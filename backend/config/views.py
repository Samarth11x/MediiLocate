"""
System-level and conversational API views for MediLocate AI.
"""

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
