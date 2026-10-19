"""
Ranking explanation and reason code generator.

Produces human-readable, transparent explanations and reason codes for why
a candidate result received its rank.
"""

from __future__ import annotations

from typing import List, Optional


class RankingReasonCode:
    """Standardized machine-readable ranking reason codes."""
    EXACT_MATCH = "EXACT_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    FUZZY_MATCH = "FUZZY_MATCH"
    IN_STOCK_CONFIRMED = "IN_STOCK_CONFIRMED"
    LOW_STOCK_WARNING = "LOW_STOCK_WARNING"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    STALE_STOCK_CAUTION = "STALE_STOCK_CAUTION"
    UNKNOWN_STOCK = "UNKNOWN_STOCK"
    PROXIMITY_ADVANTAGE = "PROXIMITY_ADVANTAGE"
    DISTANCE_UNAVAILABLE = "DISTANCE_UNAVAILABLE"
    PRICE_COMPETITIVE = "PRICE_COMPETITIVE"
    PRICE_UNAVAILABLE = "PRICE_UNAVAILABLE"


def generate_explanation(
    match_score: float,
    display_status: str,
    distance_km: Optional[float],
    unit_price: Optional[float],
    reason_codes: List[str],
) -> str:
    """
    Construct a concise human-readable explanation sentence summarizing the rank.

    Args:
        match_score: Relevance score (0.0 - 1.0).
        display_status: User-facing stock status ('AVAILABLE', 'LOW_STOCK', 'OUTDATED', etc.).
        distance_km: Distance to pharmacy, or None.
        unit_price: Price per unit, or None.
        reason_codes: List of attached reason codes.

    Returns:
        Readable summary explanation.
    """
    parts = []

    # Relevance note
    if match_score >= 1.0:
        parts.append("Exact medicine match")
    elif match_score >= 0.85:
        parts.append("Strong medicine match")
    else:
        parts.append("Approximate medicine match")

    # Availability note
    if display_status == "AVAILABLE":
        parts.append("in stock")
    elif display_status == "LOW_STOCK":
        parts.append("low stock (< 10 units)")
    elif display_status == "OUTDATED":
        parts.append("unconfirmed stock (outdated)")
    elif display_status == "OUT_OF_STOCK":
        parts.append("out of stock")
    else:
        parts.append("unknown stock level")

    # Distance note
    if distance_km is not None:
        parts.append(f"{distance_km:.1f} km away")
    else:
        parts.append("distance unknown")

    # Price note
    if unit_price is not None:
        parts.append(f"₹{unit_price:.2f}")

    return "; ".join(parts) + "."
