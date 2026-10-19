"""
Standardized conversational responses and prompt templates for MediBot.
"""

from __future__ import annotations

from typing import Any, Dict, List

GREETING_MESSAGE = (
    "Hello! I am MediBot, your medicine discovery assistant. "
    "I can help you search for medicines by brand or generic name, understand availability statuses, "
    "and explain how MediLocate helps you locate needed prescriptions. "
    "What medicine or topic can I assist you with today?"
)

GREETING_SUGGESTIONS = [
    "Find Paracetamol 500mg",
    "How does MediLocate work?",
    "What does low stock mean?",
]

HOW_IT_WORKS_MESSAGE = (
    "MediLocate is an intelligent healthcare platform designed to help patients find medicines:\n\n"
    "1. Search: Search by commercial brand name, active generic ingredient, dosage, or form.\n"
    "2. Locate: Discover nearby pharmacies stocking your required formulation.\n"
    "3. Verify: Review real-time stock levels and verification timestamps so you never make unnecessary trips.\n\n"
    "Please note: MediBot provides informational location assistance and never prescribes, diagnoses, or sells medicines directly."
)

HOW_IT_WORKS_SUGGESTIONS = [
    "Search for a medicine",
    "What does low stock mean?",
    "How can my pharmacy join?",
]

PHARMACY_ONBOARDING_MESSAGE = (
    "Licensed retail pharmacies will be able to partner with MediLocate to list their establishments, "
    "publish verified inventory, and help patients in their neighbourhood find urgent medications. "
    "Pharmacy self-registration and dashboard tools are currently scheduled for rollout in an upcoming phase."
)

PHARMACY_ONBOARDING_SUGGESTIONS = [
    "How does MediLocate work?",
    "Search for a medicine",
]

AVAILABILITY_HELP_MESSAGE = (
    "In MediLocate, availability statuses are calculated dynamically to provide clear transparency:\n\n"
    "• AVAILABLE: The pharmacy has confirmed healthy stock (10+ units).\n"
    "• LOW STOCK: Less than 10 units remain. We strongly recommend contacting the pharmacy before travelling.\n"
    "• OUT OF STOCK: Confirmed zero units currently available.\n"
    "• OUTDATED / UNCONFIRMED: The inventory record is older than 24 hours and cannot be verified as current.\n"
    "• UNKNOWN: The pharmacy has not reported inventory counts for this medicine."
)

AVAILABILITY_HELP_SUGGESTIONS = [
    "Find Paracetamol 500mg",
    "How does MediLocate work?",
]

UNKNOWN_QUERY_MESSAGE = (
    "I'm sorry, I didn't quite catch that. As your medicine locator assistant, I can help you search for medications, "
    "explain inventory availability levels, or explain how MediLocate works. "
    "Which of these can I help you with?"
)

UNKNOWN_SUGGESTIONS = [
    "Find a medicine",
    "How does MediLocate work?",
    "What does low stock mean?",
]

MEDICINE_CLARIFICATION_MESSAGE = (
    "Which medicine or formulation are you looking for? "
    "You can tell me the brand name (e.g., 'Crocin', 'Dolo 650') or generic chemical name (e.g., 'Paracetamol 500mg', 'Amoxicillin')."
)

MEDICINE_CLARIFICATION_SUGGESTIONS = [
    "Paracetamol 500mg",
    "Amoxicillin 500mg",
    "Cetirizine 10mg",
]


def format_medicine_search_response(
    query: str,
    matches: List[Dict[str, Any]],
) -> str:
    """
    Format medicine search matches into a friendly bulleted list.
    """
    lines = [f"I found {len(matches)} matching medicine(s) for '{query}':\n"]
    for idx, item in enumerate(matches, start=1):
        med = item.get("medicine") or {}
        brand = med.get("brand_name") or "Unknown Brand"
        generic = med.get("generic_name") or "Unknown Generic"
        strength = med.get("strength") or ""
        form = med.get("dosage_form") or ""
        details = f"{strength} {form}".strip()
        details_str = f" - {details}" if details else ""
        lines.append(f"{idx}. {brand} ({generic}){details_str}")

    lines.append("\nNote: Stock availability at local pharmacies will be displayed when searching nearby locations.")
    return "\n".join(lines)
