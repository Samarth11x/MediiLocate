"""
Rule-based intent classifier for MediBot.

Lightweight, deterministic intent recognition reusing Core Intelligence normalization
and prioritizing medical safety guardrails.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from core_intelligence.search_engine.normalization import normalize_query
from medibot.safety.emergency import check_emergency
from medibot.safety.safety_rules import check_medical_advice
from medibot.intents.patterns import (
    IntentType,
    GREETING_PATTERN,
    HOW_IT_WORKS_PATTERN,
    PHARMACY_ONBOARDING_PATTERN,
    AVAILABILITY_HELP_PATTERN,
    PHARMACY_SEARCH_PATTERN,
    GENERIC_MEDICINE_QUERY_PATTERN,
    MEDICINE_SEARCH_PREFIX_PATTERN,
)


@dataclass
class IntentResult:
    """
    Structured outcome of classifying a user message.
    """
    intent: str
    confidence: float
    extracted_entity: Optional[str] = None
    reason: str = ""


def classify_intent(message: str) -> IntentResult:
    """
    Classify user message into a supported intent category.

    Precedence order:
    1. EMERGENCY_CONCERN (highest priority safety guardrail)
    2. MEDICAL_ADVICE (second priority safety guardrail)
    3. HOW_IT_WORKS / PHARMACY_ONBOARDING / AVAILABILITY_HELP
    4. PHARMACY_SEARCH
    5. MEDICINE_SEARCH
    6. GREETING
    7. UNKNOWN

    Args:
        message: Cleaned user input text.

    Returns:
        IntentResult dataclass.
    """
    if not message or not isinstance(message, str):
        return IntentResult(
            intent=IntentType.UNKNOWN,
            confidence=0.0,
            reason="Empty or non-string message",
        )

    # 1. Safety Guardrail: Acute Emergency Detection
    emergency_resp = check_emergency(message)
    if emergency_resp is not None:
        return IntentResult(
            intent=IntentType.EMERGENCY_CONCERN,
            confidence=1.0,
            reason="Triggered emergency safety keyword",
        )

    # 2. Safety Guardrail: Medical Advice / Prescribing Detection
    advice_resp = check_medical_advice(message)
    if advice_resp is not None:
        return IntentResult(
            intent=IntentType.MEDICAL_ADVICE,
            confidence=1.0,
            reason="Triggered medical advice safety filter",
        )

    normalized = normalize_query(message)

    # 3. Informational & FAQ Queries
    if HOW_IT_WORKS_PATTERN.search(normalized):
        return IntentResult(
            intent=IntentType.HOW_IT_WORKS,
            confidence=0.95,
            reason="Matched how it works pattern",
        )

    if PHARMACY_ONBOARDING_PATTERN.search(normalized):
        return IntentResult(
            intent=IntentType.PHARMACY_ONBOARDING,
            confidence=0.95,
            reason="Matched pharmacy onboarding pattern",
        )

    if AVAILABILITY_HELP_PATTERN.search(normalized):
        return IntentResult(
            intent=IntentType.AVAILABILITY_HELP,
            confidence=0.95,
            reason="Matched availability help pattern",
        )

    # 4. Pharmacy Search
    if PHARMACY_SEARCH_PATTERN.search(normalized):
        return IntentResult(
            intent=IntentType.PHARMACY_SEARCH,
            confidence=0.90,
            reason="Matched pharmacy search pattern",
        )

    # 5. Medicine Search
    # Check for generic "find a medicine" (no specific name provided)
    if GENERIC_MEDICINE_QUERY_PATTERN.match(normalized):
        return IntentResult(
            intent=IntentType.MEDICINE_SEARCH,
            confidence=0.90,
            extracted_entity=None,
            reason="Generic medicine search request without entity",
        )

    # Check for prefix match e.g. "find paracetamol 500mg" or "search for amoxicillin"
    prefix_match = MEDICINE_SEARCH_PREFIX_PATTERN.match(normalized)
    if prefix_match:
        entity = prefix_match.group(1).strip()
        # Ensure the extracted entity isn't just "pharmacies" or "pharmacy"
        if not re.search(r"^(?:pharmacies|pharmacy|chemist|chemists)$", entity, re.IGNORECASE):
            return IntentResult(
                intent=IntentType.MEDICINE_SEARCH,
                confidence=0.95,
                extracted_entity=entity,
                reason="Matched medicine search command with entity",
            )

    # If it mentions standard medicine forms/units or common names directly
    common_med_terms = re.compile(
        r"\b(?:tablet|tablets|capsule|capsules|syrup|injection|mg|mcg|paracetamol|dolo|crocin|amoxicillin|ibuprofen|cetirizine|augmentin|brufen|cetzine|calpol|aspirin)\b",
        re.IGNORECASE,
    )
    if common_med_terms.search(normalized):
        return IntentResult(
            intent=IntentType.MEDICINE_SEARCH,
            confidence=0.85,
            extracted_entity=normalized,
            reason="Identified medicine-identifying keywords in query",
        )

    # 6. Greeting
    if GREETING_PATTERN.match(normalized):
        return IntentResult(
            intent=IntentType.GREETING,
            confidence=0.95,
            reason="Matched greeting pattern",
        )

    # 7. Fallback: Unknown
    return IntentResult(
        intent=IntentType.UNKNOWN,
        confidence=0.0,
        reason="No rule-based patterns matched",
    )
