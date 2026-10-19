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


import html


def format_medicine_search_response(
    query: str,
    matches: List[Dict[str, Any]],
) -> str:
    """
    Format medicine search matches into a friendly bulleted list.
    Safely decodes any HTML/hex entities at presentation boundary.
    """
    clean_query = html.unescape(query)
    lines = [f"I found {len(matches)} matching medicine(s) for '{clean_query}':\n"]
    for idx, item in enumerate(matches, start=1):
        med = item.get("medicine") or {}
        raw_brand = med.get("brand_name") or "Unknown Brand"
        raw_generic = med.get("generic_name") or "Unknown Generic"
        raw_strength = med.get("strength") or ""
        raw_form = med.get("dosage_form") or ""

        brand = html.unescape(str(raw_brand))
        generic = html.unescape(str(raw_generic))
        strength = html.unescape(str(raw_strength))
        form = html.unescape(str(raw_form))

        details = f"{strength} {form}".strip()
        details_str = f" - {details}" if details else ""
        lines.append(f"{idx}. {brand} ({generic}){details_str}")

    lines.append("\nNote: Stock availability at local pharmacies will be displayed when searching nearby locations.")
    return "\n".join(lines)


def format_pharmacy_search_response(
    results: List[Dict[str, Any]],
    medicine_name: Optional[str] = None,
    has_location: bool = False,
) -> str:
    """
    Format pharmacy inventory search results into conversational response text.
    Respects location privacy rules (no distance claims if location not provided)
    and clearly flags simulated demo data.
    """
    if not results:
        target = f" for '{html.unescape(medicine_name)}'" if medicine_name else ""
        return f"No matching pharmacies found in the directory{target}."

    if medicine_name:
        pharmacy_plural = "pharmacies" if len(results) != 1 else "pharmacy"
        clean_name = html.unescape(medicine_name)
        header = (
            f"I found {len(results)} verified {pharmacy_plural} with inventory records for '{clean_name}'. "
            "Availability varies by pharmacy; please note the stock status shown for each listing.\n"
        )
    else:
        pharmacy_plural = "pharmacies" if len(results) != 1 else "pharmacy"
        header = (
            f"I found {len(results)} verified {pharmacy_plural} in the directory. "
            "Availability varies by pharmacy; please note the stock status shown for each listing.\n"
        )
    lines = [header]

    has_any_demo = False

    for idx, item in enumerate(results, start=1):
        # Extract pharmacy details
        pharmacy = item.get("pharmacy") or item
        raw_p_name = pharmacy.get("name") or "Unknown Pharmacy"
        p_name = html.unescape(str(raw_p_name))
        area = html.unescape(str(pharmacy.get("area") or "")).strip()
        city = html.unescape(str(pharmacy.get("city") or "")).strip()
        loc_str = f" ({area}, {city})" if area and city else f" ({area or city})" if (area or city) else ""

        is_demo = item.get("is_demo") or pharmacy.get("is_demo")
        if is_demo:
            has_any_demo = True

        line_header = f"{idx}. {p_name}{loc_str}"
        lines.append(line_header)

        # Inventory stock status
        stock_status = item.get("stock_status") or item.get("stock_state")
        stock_label = item.get("stock_status_label") or item.get("stock_label")
        qty = item.get("quantity")
        if stock_status or stock_label:
            label = stock_label or stock_status
            if stock_status == "OUT_OF_STOCK" or (qty is not None and qty == 0):
                qty_desc = " (0 available)"
            elif stock_status == "UNKNOWN" or qty is None:
                qty_desc = " (count unconfirmed)"
            elif stock_status == "LOW_STOCK":
                qty_desc = f" ({qty} left in stock)"
            else:
                qty_desc = f" ({qty} in stock)" if qty is not None else ""
            lines.append(f"   • Stock: {label}{qty_desc}")

        # Price
        price = item.get("price")
        if price is not None:
            try:
                lines.append(f"   • Price: ₹{float(price):.2f}")
            except (ValueError, TypeError):
                lines.append(f"   • Price: ₹{price}")

        # Distance (ONLY if has_location and distance_km is not None)
        dist_km = item.get("distance_km")
        if has_location and dist_km is not None:
            try:
                lines.append(f"   • Distance: ~{float(dist_km):.1f} km away")
            except (ValueError, TypeError):
                lines.append(f"   • Distance: ~{dist_km} km away")

    # Footers
    if not has_location:
        lines.append("\nNote: Device location was not shared; pharmacies are listed without proximity distance ordering.")

    if has_any_demo:
        lines.append("Demonstration Notice: Displayed pharmacies and inventory records are simulated demo data.")

    return "\n".join(lines)
