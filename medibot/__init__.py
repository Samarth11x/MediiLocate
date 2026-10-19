"""
MediLocate AI - MediBot Conversational Assistant Engine.

A rule-based, medically safe conversational assistant for medicine discovery
and pharmacy inquiries. Decoupled from web frameworks and live AI APIs.
"""

from medibot.dialogue.manager import DialogueManager, MediBotResponse
from medibot.dialogue.context import ConversationContext

__version__ = "0.1.0"

__all__ = [
    "DialogueManager",
    "MediBotResponse",
    "ConversationContext",
]
