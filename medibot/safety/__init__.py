"""
MediBot safety guardrails subpackage.
"""

from medibot.safety.input_validation import (
    validate_input,
    MAX_MESSAGE_LENGTH,
)
from medibot.safety.emergency import (
    check_emergency,
    EMERGENCY_RESPONSE_MESSAGE,
)
from medibot.safety.safety_rules import (
    check_medical_advice,
    MEDICAL_ADVICE_RESPONSE,
)

__all__ = [
    "validate_input",
    "MAX_MESSAGE_LENGTH",
    "check_emergency",
    "EMERGENCY_RESPONSE_MESSAGE",
    "check_medical_advice",
    "MEDICAL_ADVICE_RESPONSE",
]
