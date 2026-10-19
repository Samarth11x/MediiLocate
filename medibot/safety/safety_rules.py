"""
Medical advice safety guardrails for MediBot.

Ensures that MediBot strictly declines diagnosing conditions, prescribing drugs,
calculating personalized dosages, or advising changes to medications, redirecting
users to licensed healthcare practitioners.
"""

from __future__ import annotations

import re
from typing import Optional
from medibot.dialogue.context import MediBotResponse

_MEDICAL_ADVICE_PATTERNS = [
    # Treatment recommendations / Prescribing
    r"\b(?:what|which)(?:\s+medicine|\s+drug|\s+tablet|\s+medication)?\s+(?:should|can|to)\s+(?:i|we|one)?\s*(?:take|give|use|administer)\b",
    r"\b(?:what medicine cures|what medicine treats|recommend (?:a |me a )?medicine|prescribe me|what to (?:take|give) for|best medicine for)\b",
    # Dosage queries
    r"\bhow much\b.+\b(?:should|can|to)\b.+\b(?:take|give|administer|use)\b",
    r"\bwhat (?:dose|dosage)\b.+\b(?:should|can|to)\b.+\b(?:take|give|administer|use)\b",
    r"\b(?:how much (?:should i|can i|to) (?:take|give|administer|use)|what (?:dose|dosage) (?:should i|is safe|for|of)|how many (?:tablets|pills|capsules|drops|spoons)\b.+\b(?:can|should) i (?:take|give)|safe dose for)\b",
    # Alteration / Stopping medication
    r"\b(?:should i stop taking|can i stop taking|should i change my (?:dose|medication)|can i increase (?:my )?dose|skip a dose)\b",
    # Diagnostics / Symptoms
    r"\b(?:diagnose (?:me|my)|do i have (?:flu|covid|cancer|infection|diabetes)|what disease (?:do i have|causes)|why is my .+ hurting|symptoms of)\b",
    # Drug interactions & Patient suitability
    r"\b(?:can i take .+ with|is it safe to take .+ with|can i mix .+ and|safe (?:during|while) pregnancy|safe for (?:my )?(?:baby|infant|toddler|child))\b",
    # Therapeutic substitution
    r"\b(?:can i substitute|is .+ a substitute for|can i replace .+ with)\b",
]

_COMPILED_ADVICE_REGEX = re.compile("|".join(_MEDICAL_ADVICE_PATTERNS), re.IGNORECASE)

MEDICAL_ADVICE_RESPONSE = (
    "Medical Safety Notice: MediBot is an informational search assistant and cannot "
    "provide medical diagnoses, prescribe treatments, recommend dosages, or advise on drug interactions. "
    "Health decisions require individualized clinical evaluation. Please consult a qualified "
    "medical doctor or registered pharmacist for advice regarding your symptoms or medications. "
    "Once you have a prescription or medical plan, I can assist you in finding pharmacies that stock your medicine."
)


def check_medical_advice(message: str) -> Optional[MediBotResponse]:
    """
    Check if a message requests clinical or personalized medical advice.

    Args:
        message: Normalized user input string.

    Returns:
        MediBotResponse if a medical advice request is detected, otherwise None.
    """
    if not message or not isinstance(message, str):
        return None

    # Ensure questions about MediLocate features (e.g. 'what does low stock mean') are not flagged
    lower_msg = message.lower()
    if "low stock" in lower_msg or "out of stock" in lower_msg or "medilocate" in lower_msg:
        # Check if it's explicitly asking what an inventory label means
        if "what does" in lower_msg and ("stock mean" in lower_msg or "status mean" in lower_msg):
            return None

    if _COMPILED_ADVICE_REGEX.search(message):
        return MediBotResponse(
            message=MEDICAL_ADVICE_RESPONSE,
            intent="MEDICAL_ADVICE",
            status="safety_response",
            suggestions=["Consult a licensed doctor", "Ask a local pharmacist", "Search for a prescribed medicine"],
            safety_category="medical_advice",
        )

    return None
