"""
Unit tests for pure Python medicine search matching with medication identity safeguards.
"""

import pytest
from typing import List, Dict, Any
from core_intelligence.search_engine.matching import search_medicines


class TestMedicineMatching:
    """Tests covering search matching, aliases, safeguards, and deterministic ordering."""

    def test_exact_generic_match(self, synthetic_catalogue: List[Dict[str, Any]]):
        results = search_medicines("Paracetamol", synthetic_catalogue)
        assert len(results) >= 3
        # First results should be exact generic matches
        assert results[0]["match_type"] == "exact_name"
        assert results[0]["match_score"] == 1.0
        assert "generic_name" in results[0]["matched_fields"]

    def test_exact_brand_match(self, synthetic_catalogue: List[Dict[str, Any]]):
        results = search_medicines("Dolo 650", synthetic_catalogue)
        assert len(results) >= 1
        top_match = results[0]
        assert top_match["medicine"]["brand_name"] == "Dolo 650"
        assert top_match["match_score"] == 1.0
        assert "brand_name" in top_match["matched_fields"]

    def test_partial_name_match(self, synthetic_catalogue: List[Dict[str, Any]]):
        results = search_medicines("Augmentin", synthetic_catalogue)
        assert len(results) >= 1
        assert results[0]["medicine"]["brand_name"] == "Augmentin 625 Duo"
        assert results[0]["match_score"] >= 0.90
        assert "brand_name" in results[0]["matched_fields"]

    def test_alias_match(self, synthetic_catalogue: List[Dict[str, Any]]):
        # Querying by American synonym 'acetaminophen'
        results = search_medicines("acetaminophen", synthetic_catalogue)
        assert len(results) >= 2
        for r in results:
            assert r["medicine"]["generic_name"] == "Paracetamol"
            assert "search_aliases" in r["matched_fields"]

    def test_fuzzy_matching_with_threshold(self, synthetic_catalogue: List[Dict[str, Any]]):
        # Typo: 'Brufen' misspelled as 'Brufen' or 'Ibuprofn'
        results = search_medicines("Ibuprofn", synthetic_catalogue, fuzzy_threshold=0.7)
        assert len(results) >= 1
        assert results[0]["medicine"]["brand_name"] == "Brufen 400"
        assert results[0]["match_type"] == "fuzzy"
        assert results[0]["match_score"] >= 0.70

    def test_explicit_strength_safeguard(self, synthetic_catalogue: List[Dict[str, Any]]):
        """
        Critical Safeguard:
        Requesting 500mg Paracetamol must NEVER return 650mg Paracetamol as an equivalent match.
        """
        results_500 = search_medicines("Paracetamol 500mg", synthetic_catalogue)
        matched_ids_500 = [r["medicine"]["id"] for r in results_500]
        assert "syn-med-001" in matched_ids_500  # Crocin 500
        assert "syn-med-002" not in matched_ids_500  # Dolo 650 must be excluded!

        # Inversely, requesting 650mg must exclude 500mg
        results_650 = search_medicines("Paracetamol 650mg", synthetic_catalogue)
        matched_ids_650 = [r["medicine"]["id"] for r in results_650]
        assert "syn-med-002" in matched_ids_650  # Dolo 650
        assert "syn-med-001" not in matched_ids_650  # Crocin 500 must be excluded!

    def test_explicit_dosage_form_safeguard(self, synthetic_catalogue: List[Dict[str, Any]]):
        """
        Critical Safeguard:
        Requesting Syrup formulation must not silently return Tablets.
        """
        results_syrup = search_medicines("Paracetamol syrup", synthetic_catalogue)
        assert len(results_syrup) >= 1
        for r in results_syrup:
            assert r["medicine"]["dosage_form"].lower() == "syrup"
            assert r["medicine"]["brand_name"] == "Calpol Pead"

    def test_missing_optional_catalogue_fields(self):
        sparse_catalogue = [
            {"id": "sparse-1", "brand_name": "Minimal Med"},
            {"id": "sparse-2", "generic_name": "Simple Chem"},
            {"id": "sparse-3"},  # completely empty dictionary
        ]
        # Should not crash
        results = search_medicines("Minimal", sparse_catalogue)
        assert len(results) == 1
        assert results[0]["medicine"]["id"] == "sparse-1"

    def test_deterministic_ordering_and_limit(self, synthetic_catalogue: List[Dict[str, Any]]):
        results_all = search_medicines("Paracetamol", synthetic_catalogue)
        results_limit_2 = search_medicines("Paracetamol", synthetic_catalogue, limit=2)

        assert len(results_limit_2) == 2
        assert results_limit_2[0] == results_all[0]
        assert results_limit_2[1] == results_all[1]

        # Scores must be non-increasing
        scores = [r["match_score"] for r in results_all]
        assert scores == sorted(scores, reverse=True)

    def test_empty_query_returns_empty_list(self, synthetic_catalogue: List[Dict[str, Any]]):
        assert search_medicines("", synthetic_catalogue) == []
        assert search_medicines("    ", synthetic_catalogue) == []
        assert search_medicines(None, synthetic_catalogue) == []
