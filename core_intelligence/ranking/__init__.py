"""
Ranking subpackage: multi-factor scoring and transparent explanations.
"""

from core_intelligence.ranking.scoring import (
    RankingConfig,
    DEFAULT_RANKING_CONFIG,
    compute_availability_subscore,
    compute_distance_subscore,
    compute_price_subscore,
    rank_candidates,
)
from core_intelligence.ranking.explanations import (
    RankingReasonCode,
    generate_explanation,
)

__all__ = [
    "RankingConfig",
    "DEFAULT_RANKING_CONFIG",
    "compute_availability_subscore",
    "compute_distance_subscore",
    "compute_price_subscore",
    "rank_candidates",
    "RankingReasonCode",
    "generate_explanation",
]
