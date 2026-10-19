"""
Transparent result ranking and composite scoring engine.

Calculates multi-factor heuristic scores across:
1. Medicine match relevance
2. Stock availability & freshness
3. Geographic proximity
4. Pricing competitiveness

Deterministic, configurable, and completely decoupled from database and web frameworks.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from core_intelligence.availability.freshness import (
    get_display_availability,
    DisplayStatus,
)
from core_intelligence.ranking.explanations import (
    RankingReasonCode,
    generate_explanation,
)


@dataclass(frozen=True)
class RankingConfig:
    """
    Configuration parameters and weights for composite ranking.

    Relative weights must sum to 1.0.
    """
    weight_relevance: float = 0.45
    weight_availability: float = 0.30
    weight_distance: float = 0.15
    weight_price: float = 0.10
    max_distance_km: float = 50.0
    benchmark_price: float = 1000.0

    def __post_init__(self) -> None:
        weights = [
            self.weight_relevance,
            self.weight_availability,
            self.weight_distance,
            self.weight_price,
        ]
        if any(w < 0.0 for w in weights):
            raise ValueError("All ranking weights must be non-negative")
        total = sum(weights)
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Ranking weights must sum to 1.0, got {total}")
        if self.max_distance_km <= 0.0:
            raise ValueError("max_distance_km must be a positive float")
        if self.benchmark_price <= 0.0:
            raise ValueError("benchmark_price must be a positive float")


DEFAULT_RANKING_CONFIG = RankingConfig()


def compute_availability_subscore(display_status: str) -> float:
    """
    Map user-facing stock status to an availability subscore in [0.0, 1.0].

    Fresh confirmed in-stock receives highest priority; outdated/unconfirmed stock
    is penalized so it cannot masquerade as confirmed availability.
    """
    if display_status == DisplayStatus.AVAILABLE:
        return 1.0
    if display_status == DisplayStatus.LOW_STOCK:
        return 0.75
    if display_status == DisplayStatus.OUTDATED:
        # Outdated record: penalized caution score
        return 0.35
    if display_status == DisplayStatus.UNKNOWN:
        return 0.20
    if display_status == DisplayStatus.OUT_OF_STOCK:
        return 0.05
    return 0.10


def compute_distance_subscore(distance_km: Optional[float], max_distance_km: float) -> float:
    """
    Calculate normalized proximity score in [0.0, 1.0].

    Safeguard: Unavailable distance is NOT treated as 0 km. It receives a penalized
    score of 0.20 to prevent unlocatable pharmacies from dominating nearby ones.
    """
    if distance_km is None:
        return 0.20

    dist = max(0.0, float(distance_km))
    if dist >= max_distance_km:
        return 0.0
    return 1.0 - (dist / max_distance_km)


def compute_price_subscore(unit_price: Optional[Any], benchmark_price: float) -> float:
    """
    Calculate normalized price competitiveness in [0.0, 1.0].

    Safeguard: Unknown price is NOT treated as 0.0 (free). It receives a neutral score of 0.50.
    """
    if unit_price is None:
        return 0.50

    try:
        p = float(unit_price)
    except (TypeError, ValueError):
        return 0.50

    if p < 0.0:
        return 0.50
    if p >= benchmark_price:
        return 0.0
    return 1.0 - (p / benchmark_price)


def rank_candidates(
    candidates: List[Dict[str, Any]],
    current_time: Optional[datetime] = None,
    config: Optional[RankingConfig] = None,
) -> List[Dict[str, Any]]:
    """
    Rank candidate pharmacy medicine listings deterministically.

    Considers:
    - Medicine match relevance (primary priority)
    - Stock availability & freshness (confirmed fresh stock prioritized)
    - Geographic proximity (nearer preferred; missing distance not treated as 0 km)
    - Unit price (cheaper preferred; unknown price not treated as free)

    Safeguards:
    - Input list and dictionary records are NOT mutated.
    - Deterministic tie-breaking across equal scores.
    - Outdated inventory is transparently flagged and penalized.

    Args:
        candidates: List of candidate dictionaries.
        current_time: Reference datetime for freshness checks (injectable for testing).
        config: RankingConfig instance. Defaults to DEFAULT_RANKING_CONFIG.

    Returns:
        New sorted list of result dictionaries with rank and scoring explanations attached.
    """
    if not candidates:
        return []

    cfg = config or DEFAULT_RANKING_CONFIG
    scored_candidates = []

    for item in candidates:
        if not isinstance(item, dict):
            continue

        # Extract factors safely
        medicine = item.get("medicine") or {}
        pharmacy = item.get("pharmacy") or {}
        raw_match_score = item.get("match_score", 0.0)
        quantity = item.get("quantity")
        last_updated = item.get("last_updated")
        distance_km = item.get("distance_km")
        unit_price = item.get("unit_price")

        # 1. Relevance sub-score
        try:
            rel_score = max(0.0, min(1.0, float(raw_match_score)))
        except (TypeError, ValueError):
            rel_score = 0.0

        # 2. Availability & Freshness sub-score
        display_res = get_display_availability(
            quantity=quantity,
            last_updated=last_updated,
            current_time=current_time,
        )
        avail_score = compute_availability_subscore(display_res.display_status)

        # 3. Distance sub-score
        dist_score = compute_distance_subscore(distance_km, cfg.max_distance_km)

        # 4. Price sub-score
        price_score = compute_price_subscore(unit_price, cfg.benchmark_price)

        # Composite score
        composite_score = (
            (cfg.weight_relevance * rel_score)
            + (cfg.weight_availability * avail_score)
            + (cfg.weight_distance * dist_score)
            + (cfg.weight_price * price_score)
        )

        # Build reason codes
        reason_codes: List[str] = []
        if rel_score >= 1.0:
            reason_codes.append(RankingReasonCode.EXACT_MATCH)
        elif rel_score >= 0.85:
            reason_codes.append(RankingReasonCode.PARTIAL_MATCH)
        else:
            reason_codes.append(RankingReasonCode.FUZZY_MATCH)

        if display_res.display_status == DisplayStatus.AVAILABLE:
            reason_codes.append(RankingReasonCode.IN_STOCK_CONFIRMED)
        elif display_res.display_status == DisplayStatus.LOW_STOCK:
            reason_codes.append(RankingReasonCode.LOW_STOCK_WARNING)
        elif display_res.display_status == DisplayStatus.OUTDATED:
            reason_codes.append(RankingReasonCode.STALE_STOCK_CAUTION)
        elif display_res.display_status == DisplayStatus.OUT_OF_STOCK:
            reason_codes.append(RankingReasonCode.OUT_OF_STOCK)
        else:
            reason_codes.append(RankingReasonCode.UNKNOWN_STOCK)

        if distance_km is not None:
            if float(distance_km) <= 5.0:
                reason_codes.append(RankingReasonCode.PROXIMITY_ADVANTAGE)
        else:
            reason_codes.append(RankingReasonCode.DISTANCE_UNAVAILABLE)

        if unit_price is not None:
            if price_score >= 0.75:
                reason_codes.append(RankingReasonCode.PRICE_COMPETITIVE)
        else:
            reason_codes.append(RankingReasonCode.PRICE_UNAVAILABLE)

        price_float = float(unit_price) if unit_price is not None else None
        explanation = generate_explanation(
            match_score=rel_score,
            display_status=display_res.display_status,
            distance_km=distance_km,
            unit_price=price_float,
            reason_codes=reason_codes,
        )

        # Create output copy (preserving original input untouched)
        result_entry = copy.deepcopy(item)
        result_entry["ranking_score"] = round(composite_score, 4)
        result_entry["relevance_score"] = round(rel_score, 4)
        result_entry["availability_score"] = round(avail_score, 4)
        result_entry["distance_score"] = round(dist_score, 4)
        result_entry["price_score"] = round(price_score, 4)
        result_entry["display_status"] = display_res.display_status
        result_entry["is_confirmed"] = display_res.is_confirmed
        result_entry["reason_codes"] = reason_codes
        result_entry["explanation"] = explanation

        scored_candidates.append(result_entry)

    # Deterministic multi-key sorting:
    # 1. ranking_score DESC
    # 2. match_score DESC
    # 3. distance_km ASC (inf if None)
    # 4. unit_price ASC (inf if None)
    # 5. pharmacy ID ASC
    def _sort_key(c: Dict[str, Any]) -> tuple:
        r_score = c.get("ranking_score", 0.0)
        m_score = c.get("relevance_score", 0.0)
        d = c.get("distance_km")
        d_val = float(d) if d is not None else float("inf")
        p = c.get("unit_price")
        p_val = float(p) if p is not None else float("inf")
        ph_id = str((c.get("pharmacy") or {}).get("id", ""))
        return (-r_score, -m_score, d_val, p_val, ph_id)

    scored_candidates.sort(key=_sort_key)

    # Assign 1-indexed rank
    for idx, c in enumerate(scored_candidates, start=1):
        c["rank"] = idx

    return scored_candidates
