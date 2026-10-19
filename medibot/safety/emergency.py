"""
Emergency detection and safety response rules.

Detects urgent and life-threatening symptoms and situations, intercepting them
with immediate emergency care guidance rather than general conversational or search replies.
"""

from __future__ import annotations

import re
from typing import Optional
from medibot.dialogue.context import MediBotResponse

# Regex patterns matching potential acute medical emergencies
_EMERGENCY_PATTERNS = [
    # Cardiac / Chest pain
    r"\b(?:chest pain|heart attack|cardiac arrest|chest pressure|crushing chest)\b",
    # Breathing emergencies
    r"\b(?:can'?t breathe|cannot breathe|difficulty breathing|shortness of breath|choking|suffocating|severe asthma attack)\b",
    # Poisoning / Overdose
    r"\b(?:overdose|overdosed|swallowed poison|took (?:all|whole|entire) (?:the )?(?:pills|bottle|medicine)|drank poison|poisoning)\b",
    # Severe bleeding / Trauma
    r"\b(?:severe bleeding|coughing up blood|vomiting blood|hemorrhage|unconscious|passed out|fainted|unresponsive)\b",
    # Neurological / Stroke
    r"\b(?:stroke|seizure|convulsing|face drooping|sudden paralysis|loss of speech)\b",
    # Severe allergic reactions
    r"\b(?:anaphylaxis|throat (?:closing|swelling)|severe allergic reaction)\b",
    # Self-harm
    r"\b(?:suicide|kill myself|want to die|end my life|self[- ]harm)\b",
]

_COMPILED_EMERGENCY_REGEX = re.compile("|".join(_EMERGENCY_PATTERNS), re.IGNORECASE)

EMERGENCY_RESPONSE_MESSAGE = (
    "EMERGENCY ADVISORY: If you or someone near you is experiencing a life-threatening "
    "or urgent medical situation (such as severe chest pain, difficulty breathing, acute trauma, "
    "suspected overdose, or loss of consciousness), please immediately contact your local "
    "emergency medical services (such as 112 or 108 in India, 911 in North America, or your local emergency hotline) "
    "or proceed to the nearest hospital emergency room. "
    "MediBot is an informational medicine locator and cannot provide medical intervention or emergency care."
)


def check_emergency(message: str) -> Optional[MediBotResponse]:
    """
    Check if a user message indicates a potential acute medical emergency.

    Args:
        message: Normalized user input string.

    Returns:
        MediBotResponse if an emergency pattern is detected, otherwise None.
    """
    if not message or not isinstance(message, str):
        return None

    if _COMPILED_EMERGENCY_REGEX.search(message):
        return MediBotResponse(
            message=EMERGENCY_RESPONSE_MESSAGE,
            intent="EMERGENCY_CONCERN",
            status="safety_response",
            suggestions=["Call emergency services (112 / 108 / 911)", "Find nearest hospital emergency department"],
            safety_category="emergency_concern",
        )

    return None
