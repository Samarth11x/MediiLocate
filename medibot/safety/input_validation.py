"""
Input validation and sanitization for MediBot.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple
from medibot.dialogue.context import MediBotResponse

MAX_MESSAGE_LENGTH: int = 500


def validate_input(
    message: Any,
    max_length: int = MAX_MESSAGE_LENGTH,
) -> Tuple[bool, Optional[str], Optional[MediBotResponse]]:
    """
    Validate and clean user input text.

    Args:
        message: Raw input object from client.
        max_length: Maximum allowed character length (default: 500).

    Returns:
        Tuple of (is_valid, cleaned_message, error_response).
        If is_valid is True, error_response is None.
    """
    # Type check: must be string, strictly disallowing booleans, ints, dicts, etc.
    if message is None or not isinstance(message, str) or isinstance(message, bool):
        error_resp = MediBotResponse(
            message="Please provide a valid text message to chat with MediBot.",
            intent="UNKNOWN",
            status="error",
            suggestions=["Find a medicine", "How does MediLocate work?"],
            safety_category="input_validation",
        )
        return False, None, error_resp

    cleaned = message.strip()

    # Empty check
    if not cleaned:
        error_resp = MediBotResponse(
            message="It looks like you sent an empty message. How can I help you find medicines or pharmacies today?",
            intent="UNKNOWN",
            status="needs_clarification",
            suggestions=["Find Paracetamol 500mg", "Pharmacies near me", "How does MediLocate work?"],
            safety_category="input_validation",
        )
        return False, None, error_resp

    # Length check
    if len(cleaned) > max_length:
        error_resp = MediBotResponse(
            message=(
                f"Your message exceeds the maximum allowed length of {max_length} characters. "
                "Please shorten your question so I can assist you effectively."
            ),
            intent="UNKNOWN",
            status="error",
            suggestions=["Search for a medicine", "Find nearby pharmacies"],
            safety_category="input_validation",
        )
        return False, None, error_resp

    return True, cleaned, None
