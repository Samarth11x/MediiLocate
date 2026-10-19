"""
Pattern definitions and compiled regular expressions for MediBot intent classification.
"""

from __future__ import annotations

import re

# Supported intent string constants
class IntentType:
    EMERGENCY_CONCERN = "EMERGENCY_CONCERN"
    MEDICAL_ADVICE = "MEDICAL_ADVICE"
    GREETING = "GREETING"
    MEDICINE_SEARCH = "MEDICINE_SEARCH"
    PHARMACY_SEARCH = "PHARMACY_SEARCH"
    HOW_IT_WORKS = "HOW_IT_WORKS"
    PHARMACY_ONBOARDING = "PHARMACY_ONBOARDING"
    AVAILABILITY_HELP = "AVAILABILITY_HELP"
    UNKNOWN = "UNKNOWN"


# Greetings
GREETING_PATTERN = re.compile(
    r"^(?:hi|hello|hey|good (?:morning|afternoon|evening)|howdy|greetings|hola)(?:\s+(?:medibot|there|bot))?[!.]*$",
    re.IGNORECASE,
)

# How it works
HOW_IT_WORKS_PATTERN = re.compile(
    r"\b(?:how (?:does |do )?(?:medilocate|this platform|this app|the app|it) work|what is medilocate|tell me about medilocate|about medilocate)\b",
    re.IGNORECASE,
)

# Pharmacy Onboarding
PHARMACY_ONBOARDING_PATTERN = re.compile(
    r"\b(?:how (?:can|does) (?:a |my |our )?pharmacy (?:join|register|onboard|sign up)|partner with medilocate|register (?:a |my |our )?pharmacy|pharmacy onboarding|pharmacy registration|pharmacy sign up|list (?:a |my |our )?pharmacy)\b",
    re.IGNORECASE,
)

# Availability status explanation
AVAILABILITY_HELP_PATTERN = re.compile(
    r"\b(?:what (?:does|is) (?:low stock|out of stock|available|unknown) (?:mean|status)|what does low stock mean|what is low stock|explain (?:stock|availability) status|how is stock (?:checked|calculated))\b",
    re.IGNORECASE,
)

# Pharmacy search (asking for stores, chemists, pharmacies)
PHARMACY_SEARCH_PATTERN = re.compile(
    r"\b(?:find|search|show|locate|nearby|near me|nearest|closest)\b.*\b(?:pharmacy|pharmacies|chemist|chemists|medical store|medical stores|drugstore|drugstores)\b"
    r"|\b(?:pharmacies|chemists|medical stores) (?:near me|nearby|in my area|around here)\b",
    re.IGNORECASE,
)

# Generic Medicine Search cues (e.g. "find a medicine", "search for a medicine", "lookup medicine")
GENERIC_MEDICINE_QUERY_PATTERN = re.compile(
    r"^(?:find|search|lookup|look for|locate|need|want|get)\s+(?:(?:a|for a|me a|for)\s+)?(?:medicine|medicines|drug|drugs|tablet|tablets|prescription)[!.]*$",
    re.IGNORECASE,
)

# Specific Medicine search prefixes
MEDICINE_SEARCH_PREFIX_PATTERN = re.compile(
    r"^(?:find|search for|search|lookup|look for|locate|do you have|where can i find|where can i get|i need|i want|check stock of)\s+(.+)$",
    re.IGNORECASE,
)
