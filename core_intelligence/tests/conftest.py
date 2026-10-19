"""
Test fixtures and synthetic mock data for Core Intelligence pytest suite.

All records in this fixture are STRICTLY SYNTHETIC and designed solely for
offline mathematical and algorithmic validation. They do not seed or reflect
real-world production database tables.
"""

import pytest
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any


@pytest.fixture
def fixed_now() -> datetime:
    """
    Fixed reference timestamp for deterministic freshness and ranking tests.
    """
    return datetime(2026, 10, 19, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def synthetic_catalogue() -> List[Dict[str, Any]]:
    """
    Synthetic medicine catalogue covering varied brand names, generic formulations,
    dosages, and aliases for search matching validation.
    """
    return [
        {
            "id": "syn-med-001",
            "generic_name": "Paracetamol",
            "brand_name": "Crocin 500",
            "strength": "500 mg",
            "dosage_form": "Tablet",
            "search_aliases": ["crocin", "acetaminophen", "fever relief"],
            "manufacturer": "Synthetic Pharma Ltd",
            "category": "Analgesic",
        },
        {
            "id": "syn-med-002",
            "generic_name": "Paracetamol",
            "brand_name": "Dolo 650",
            "strength": "650 mg",
            "dosage_form": "Tablet",
            "search_aliases": ["dolo", "acetaminophen 650", "fever"],
            "manufacturer": "Synthetic Labs",
            "category": "Analgesic",
        },
        {
            "id": "syn-med-003",
            "generic_name": "Paracetamol",
            "brand_name": "Calpol Pead",
            "strength": "250 mg / 5 ml",
            "dosage_form": "Syrup",
            "search_aliases": ["calpol", "pediatric paracetamol", "baby fever"],
            "manufacturer": "Synthetic Health",
            "category": "Antipyretic",
        },
        {
            "id": "syn-med-004",
            "generic_name": "Amoxicillin",
            "brand_name": "Mox 500",
            "strength": "500 mg",
            "dosage_form": "Capsule",
            "search_aliases": ["amoxycillin", "mox", "antibiotic"],
            "manufacturer": "Synthetic Bio",
            "category": "Antibiotic",
        },
        {
            "id": "syn-med-005",
            "generic_name": "Amoxicillin and Clavulanate",
            "brand_name": "Augmentin 625 Duo",
            "strength": "625 mg",
            "dosage_form": "Tablet",
            "search_aliases": ["augmentin", "co-amoxiclav", "amox-clav"],
            "manufacturer": "Synthetic Bio",
            "category": "Antibiotic",
        },
        {
            "id": "syn-med-006",
            "generic_name": "Ibuprofen",
            "brand_name": "Brufen 400",
            "strength": "400 mg",
            "dosage_form": "Tablet",
            "search_aliases": ["brufen", "pain relief", "nsaid"],
            "manufacturer": "Synthetic Therapeutics",
            "category": "Analgesic",
        },
        {
            "id": "syn-med-007",
            "generic_name": "Cetirizine Hydrochloride",
            "brand_name": "Cetzine",
            "strength": "10 mg",
            "dosage_form": "Tablet",
            "search_aliases": ["cetzine", "allergy", "antihistamine"],
            "manufacturer": "Synthetic Remedies",
            "category": "Antihistamine",
        },
        {
            "id": "syn-med-008",
            "generic_name": "Cough Mixture",
            "brand_name": "Benadryl Cough",
            "strength": "100 ml",
            "dosage_form": "Syrup",
            "search_aliases": ["cough syrup", "benadryl"],
            "manufacturer": "Synthetic Consumer",
            "category": "Antitussive",
        },
    ]


@pytest.fixture
def synthetic_candidates(fixed_now: datetime) -> List[Dict[str, Any]]:
    """
    Synthetic pharmacy candidates for ranking tests.
    """
    return [
        {
            "id": "cand-001",
            "pharmacy": {"id": "pharm-alpha", "name": "Alpha Care Pharmacy"},
            "medicine": {"id": "syn-med-001", "brand_name": "Crocin 500"},
            "match_score": 1.0,
            "quantity": 25,
            "last_updated": fixed_now - timedelta(hours=2),  # Fresh available
            "distance_km": 1.2,
            "unit_price": 20.00,
        },
        {
            "id": "cand-002",
            "pharmacy": {"id": "pharm-beta", "name": "Beta Health Chemists"},
            "medicine": {"id": "syn-med-001", "brand_name": "Crocin 500"},
            "match_score": 1.0,
            "quantity": 4,
            "last_updated": fixed_now - timedelta(hours=3),  # Fresh low stock
            "distance_km": 0.8,
            "unit_price": 22.00,
        },
        {
            "id": "cand-003",
            "pharmacy": {"id": "pharm-gamma", "name": "Gamma Super Meds"},
            "medicine": {"id": "syn-med-001", "brand_name": "Crocin 500"},
            "match_score": 1.0,
            "quantity": 50,
            "last_updated": fixed_now - timedelta(days=3),  # Stale stock!
            "distance_km": 0.5,
            "unit_price": 18.00,
        },
        {
            "id": "cand-004",
            "pharmacy": {"id": "pharm-delta", "name": "Delta 24/7 Meds"},
            "medicine": {"id": "syn-med-001", "brand_name": "Crocin 500"},
            "match_score": 1.0,
            "quantity": 0,
            "last_updated": fixed_now - timedelta(hours=1),  # Out of stock
            "distance_km": 0.3,
            "unit_price": 20.00,
        },
        {
            "id": "cand-005",
            "pharmacy": {"id": "pharm-epsilon", "name": "Epsilon Distant Pharma"},
            "medicine": {"id": "syn-med-001", "brand_name": "Crocin 500"},
            "match_score": 1.0,
            "quantity": 100,
            "last_updated": fixed_now - timedelta(hours=1),  # Available but far
            "distance_km": 15.0,
            "unit_price": 15.00,
        },
    ]
