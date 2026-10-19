"""
Fixtures and mock doubles for MediBot unit tests.

All data here is purely synthetic for unit testing and does not reflect
production databases.
"""

import pytest
from typing import Any, Dict, List

from medibot.dialogue.manager import DialogueManager
from medibot.tools.medicine_search import MedicineSearchTool
from medibot.tools.pharmacy_search import PharmacySearchTool


@pytest.fixture
def synthetic_medicine_catalogue() -> List[Dict[str, Any]]:
    """Synthetic medicine entries for tool testing."""
    return [
        {
            "id": "med-syn-01",
            "generic_name": "Paracetamol",
            "brand_name": "Crocin 500",
            "strength": "500 mg",
            "dosage_form": "Tablet",
            "search_aliases": ["crocin", "acetaminophen"],
        },
        {
            "id": "med-syn-02",
            "generic_name": "Paracetamol",
            "brand_name": "Dolo 650",
            "strength": "650 mg",
            "dosage_form": "Tablet",
            "search_aliases": ["dolo"],
        },
        {
            "id": "med-syn-03",
            "generic_name": "Amoxicillin",
            "brand_name": "Mox 500",
            "strength": "500 mg",
            "dosage_form": "Capsule",
            "search_aliases": ["mox"],
        },
        {
            "id": "med-syn-04",
            "generic_name": "Paracetamol",
            "brand_name": "Calpol Pead",
            "strength": "250 mg / 5 ml",
            "dosage_form": "Syrup",
            "search_aliases": ["calpol", "pediatric"],
        },
    ]


@pytest.fixture
def connected_medicine_tool(synthetic_medicine_catalogue: List[Dict[str, Any]]) -> MedicineSearchTool:
    """Medicine tool connected to synthetic catalogue."""
    return MedicineSearchTool(catalogue_provider=synthetic_medicine_catalogue)


@pytest.fixture
def empty_medicine_tool() -> MedicineSearchTool:
    """Medicine tool connected to an empty catalogue."""
    return MedicineSearchTool(catalogue_provider=[])


@pytest.fixture
def disconnected_medicine_tool() -> MedicineSearchTool:
    """Medicine tool with no catalogue provider attached."""
    return MedicineSearchTool(catalogue_provider=None)


@pytest.fixture
def default_pharmacy_tool() -> PharmacySearchTool:
    """Standard pharmacy tool (not connected in Phase 5)."""
    return PharmacySearchTool(pharmacy_provider=None)


@pytest.fixture
def test_dialogue_manager(connected_medicine_tool: MedicineSearchTool, default_pharmacy_tool: PharmacySearchTool) -> DialogueManager:
    """Configured DialogueManager for full workflow unit testing."""
    return DialogueManager(
        medicine_tool=connected_medicine_tool,
        pharmacy_tool=default_pharmacy_tool,
        max_message_length=500,
    )
