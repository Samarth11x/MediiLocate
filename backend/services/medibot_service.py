"""
MediBot dialogue manager service factory for Django backend.

Provides configured DialogueManager instances with injected Django tools.
"""

from __future__ import annotations

try:
    from services.medibot_tools import (
        get_django_medicine_search_tool,
        get_django_pharmacy_search_tool,
    )
except ImportError:
    from backend.services.medibot_tools import (
        get_django_medicine_search_tool,
        get_django_pharmacy_search_tool,
    )

from medibot.dialogue.manager import DialogueManager


def get_medibot_dialogue_manager() -> DialogueManager:
    """
    Factory creating a configured MediBot DialogueManager.
    Injects Django medicine search tool and placeholder pharmacy tool.
    """
    medicine_tool = get_django_medicine_search_tool()
    pharmacy_tool = get_django_pharmacy_search_tool()
    return DialogueManager(
        medicine_tool=medicine_tool,
        pharmacy_tool=pharmacy_tool,
    )
