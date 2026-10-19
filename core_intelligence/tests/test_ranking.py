"""
Unit tests for transparent result ranking and multi-factor composite scoring.
"""

import copy
import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any

from core_intelligence.ranking.scoring import (
    RankingConfig,
    rank_candidates,
    compute_availability_subscore,
    compute_distance_subscore,
    compute_price_subscore,
)
from core_intelligence.ranking.explanations import RankingReasonCode


class TestRankingLogic:
    """Tests for multi-factor ranking, safeguards, immutability, and explanations."""

    def test_relevance_dominates_over_cheap_irrelevant(self, fixed_now: datetime):
        """
        Critical Safeguard:
        An exact match (relevance=1.0) must outrank a cheap/near but irrelevant match (relevance=0.2).
        """
        candidates = [
            {
                "id": "c-irrelevant",
                "pharmacy": {"id": "p-cheap", "name": "Cheap Pharmacy"},
                "medicine": {"brand_name": "Irrelevant Syrup"},
                "match_score": 0.20,
                "quantity": 100,
                "last_updated": fixed_now - timedelta(hours=1),
                "distance_km": 0.2,
                "unit_price": 5.00,
            },
            {
                "id": "c-exact",
                "pharmacy": {"id": "p-target", "name": "Target Pharmacy"},
                "medicine": {"brand_name": "Crocin 500"},
                "match_score": 1.0,
                "quantity": 15,
                "last_updated": fixed_now - timedelta(hours=2),
                "distance_km": 2.0,
                "unit_price": 25.00,
            },
        ]

        ranked = rank_candidates(candidates, current_time=fixed_now)
        assert ranked[0]["id"] == "c-exact"
        assert ranked[0]["ranking_score"] > ranked[1]["ranking_score"]

    def test_fresh_available_outranks_stale_stock(self, fixed_now: datetime):
        """
        A pharmacy with fresh verified stock must outrank a pharmacy with stale unconfirmed stock.
        """
        candidates = [
            {
                "id": "c-stale",
                "pharmacy": {"id": "p-stale", "name": "Stale Records Chemist"},
                "match_score": 1.0,
                "quantity": 100,
                "last_updated": fixed_now - timedelta(days=5),  # 5 days stale!
                "distance_km": 1.0,
                "unit_price": 20.00,
            },
            {
                "id": "c-fresh",
                "pharmacy": {"id": "p-fresh", "name": "Fresh Verified Chemist"},
                "match_score": 1.0,
                "quantity": 20,
                "last_updated": fixed_now - timedelta(hours=1),  # fresh!
                "distance_km": 1.2,
                "unit_price": 20.00,
            },
        ]

        ranked = rank_candidates(candidates, current_time=fixed_now)
        assert ranked[0]["id"] == "c-fresh"
        assert ranked[0]["display_status"] == "AVAILABLE"
        assert ranked[0]["is_confirmed"] is True

        # Stale candidate must be marked OUTDATED and unconfirmed
        assert ranked[1]["id"] == "c-stale"
        assert ranked[1]["display_status"] == "OUTDATED"
        assert ranked[1]["is_confirmed"] is False
        assert RankingReasonCode.STALE_STOCK_CAUTION in ranked[1]["reason_codes"]

    def test_distance_proximity_ordering(self, fixed_now: datetime):
        """
        When relevance and availability are equal, closer pharmacy ranks higher.
        """
        candidates = [
            {
                "id": "c-far",
                "pharmacy": {"id": "p-far"},
                "match_score": 1.0,
                "quantity": 30,
                "last_updated": fixed_now - timedelta(hours=1),
                "distance_km": 12.0,
                "unit_price": 20.00,
            },
            {
                "id": "c-near",
                "pharmacy": {"id": "p-near"},
                "match_score": 1.0,
                "quantity": 30,
                "last_updated": fixed_now - timedelta(hours=1),
                "distance_km": 1.5,
                "unit_price": 20.00,
            },
        ]

        ranked = rank_candidates(candidates, current_time=fixed_now)
        assert ranked[0]["id"] == "c-near"
        assert ranked[1]["id"] == "c-far"
        assert RankingReasonCode.PROXIMITY_ADVANTAGE in ranked[0]["reason_codes"]

    def test_price_tie_breaking(self, fixed_now: datetime):
        """
        When relevance, availability, and distance are equal, cheaper price breaks the tie.
        """
        candidates = [
            {
                "id": "c-expensive",
                "pharmacy": {"id": "p-exp"},
                "match_score": 1.0,
                "quantity": 25,
                "last_updated": fixed_now - timedelta(hours=1),
                "distance_km": 2.0,
                "unit_price": 50.00,
            },
            {
                "id": "c-affordable",
                "pharmacy": {"id": "p-aff"},
                "match_score": 1.0,
                "quantity": 25,
                "last_updated": fixed_now - timedelta(hours=1),
                "distance_km": 2.0,
                "unit_price": 25.00,
            },
        ]

        ranked = rank_candidates(candidates, current_time=fixed_now)
        assert ranked[0]["id"] == "c-affordable"
        assert ranked[1]["id"] == "c-expensive"

    def test_missing_distance_not_treated_as_zero_km(self):
        # Missing distance receives a default penalty score (0.20), not a perfect 0 km score (1.0)
        assert compute_distance_subscore(None, max_distance_km=50.0) == 0.20
        assert compute_distance_subscore(0.0, max_distance_km=50.0) == 1.0

    def test_missing_price_not_treated_as_free(self):
        # Missing price receives neutral score (0.50), not a free item score (1.0)
        assert compute_price_subscore(None, benchmark_price=1000.0) == 0.50
        assert compute_price_subscore(0.0, benchmark_price=1000.0) == 1.0

    def test_input_immutability(self, synthetic_candidates: List[Dict[str, Any]], fixed_now: datetime):
        """
        Crucial: rank_candidates must NEVER mutate the original input candidates list or dicts.
        """
        candidates_backup = copy.deepcopy(synthetic_candidates)
        ranked = rank_candidates(synthetic_candidates, current_time=fixed_now)

        # Original list and items must remain completely unchanged
        assert synthetic_candidates == candidates_backup
        # Output should have rank, ranking_score, explanation
        assert "rank" in ranked[0]
        assert "ranking_score" in ranked[0]
        assert "explanation" in ranked[0]

    def test_synthetic_candidates_fixture_ranks_cleanly(
        self,
        synthetic_candidates: List[Dict[str, Any]],
        fixed_now: datetime,
    ):
        ranked = rank_candidates(synthetic_candidates, current_time=fixed_now)
        assert len(ranked) == len(synthetic_candidates)
        ranks = [r["rank"] for r in ranked]
        assert ranks == [1, 2, 3, 4, 5]

        # Top candidate must be cand-001 (Alpha Care, fresh available, 1.2km)
        assert ranked[0]["id"] == "cand-001"

    def test_invalid_weights_config(self):
        with pytest.raises(ValueError, match="sum to 1.0"):
            RankingConfig(weight_relevance=0.8, weight_availability=0.5)
        with pytest.raises(ValueError, match="non-negative"):
            RankingConfig(weight_relevance=-0.1, weight_availability=0.5, weight_distance=0.3, weight_price=0.3)
