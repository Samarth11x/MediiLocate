"""
MediLocate AI - Core Intelligence Engine
Pure Python package for medicine normalization, search matching,
availability classification, freshness validation, geospatial distance, and ranking.

Zero dependencies on Django, database drivers, network requests, or frontend frameworks.
"""

from core_intelligence.search_engine.normalization import (
    normalize_text,
    normalize_strength,
    normalize_query,
    tokenize,
    extract_strength_and_form,
)
from core_intelligence.search_engine.matching import (
    search_medicines,
    MedicineMatchResult,
)
from core_intelligence.availability.rules import (
    AvailabilityStatus,
    AvailabilityConfig,
    classify_availability,
    validate_quantity,
)
from core_intelligence.availability.freshness import (
    FreshnessStatus,
    DisplayStatus,
    FreshnessResult,
    DisplayAvailabilityResult,
    evaluate_freshness,
    get_display_availability,
)
from core_intelligence.location.distance import (
    haversine_km,
    calculate_distance_safe,
    filter_by_radius,
)
from core_intelligence.ranking.scoring import (
    RankingConfig,
    rank_candidates,
)
from core_intelligence.ranking.explanations import (
    RankingReasonCode,
    generate_explanation,
)

__version__ = "0.1.0"

__all__ = [
    "normalize_text",
    "normalize_strength",
    "normalize_query",
    "tokenize",
    "extract_strength_and_form",
    "search_medicines",
    "MedicineMatchResult",
    "AvailabilityStatus",
    "AvailabilityConfig",
    "classify_availability",
    "validate_quantity",
    "FreshnessStatus",
    "DisplayStatus",
    "FreshnessResult",
    "DisplayAvailabilityResult",
    "evaluate_freshness",
    "get_display_availability",
    "haversine_km",
    "calculate_distance_safe",
    "filter_by_radius",
    "RankingConfig",
    "rank_candidates",
    "RankingReasonCode",
    "generate_explanation",
]
