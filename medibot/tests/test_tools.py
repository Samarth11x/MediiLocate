"""
Unit tests for MediBot tool adapters and Core Intelligence integration.
"""

import pytest
from typing import Any, Dict, List
from medibot.tools.medicine_search import MedicineSearchTool
from medibot.tools.pharmacy_search import PharmacySearchTool


class TestMedicineSearchTool:
    """Tests covering Core Intelligence reuse, safeguards, and honest availability states."""

    def test_search_exact_medicine(self, connected_medicine_tool: MedicineSearchTool):
        res = connected_medicine_tool.search("Crocin 500")
        assert res.status == "success"
        assert len(res.data) >= 1
        assert res.data[0]["medicine"]["brand_name"] == "Crocin 500"

    def test_search_with_strength_safeguard(self, connected_medicine_tool: MedicineSearchTool):
        # 500mg should match Crocin 500 (500mg) and exclude Dolo 650 (650mg)
        res = connected_medicine_tool.search("Paracetamol 500mg")
        assert res.status == "success"
        matched_brands = [item["medicine"]["brand_name"] for item in res.data]
        assert "Crocin 500" in matched_brands
        assert "Dolo 650" not in matched_brands

    def test_search_no_results(self, connected_medicine_tool: MedicineSearchTool):
        res = connected_medicine_tool.search("NonexistentMedicine123")
        assert res.status == "no_results"
        assert len(res.data) == 0
        assert "no medicines found" in res.message.lower()

    def test_search_empty_catalogue_returns_unavailable(self, empty_medicine_tool: MedicineSearchTool):
        res = empty_medicine_tool.search("Paracetamol")
        assert res.status == "unavailable"
        assert "unpopulated" in res.message.lower()

    def test_search_disconnected_provider_returns_unavailable(self, disconnected_medicine_tool: MedicineSearchTool):
        res = disconnected_medicine_tool.search("Paracetamol")
        assert res.status == "unavailable"
        assert "not connected" in res.message.lower()

    def test_search_empty_query_string(self, connected_medicine_tool: MedicineSearchTool):
        res = connected_medicine_tool.search("")
        assert res.status == "no_results"
        res_spaces = connected_medicine_tool.search("   ")
        assert res_spaces.status == "no_results"

    def test_search_provider_exception_returns_error(self):
        def crashing_provider():
            raise RuntimeError("Database connection timed out")

        tool = MedicineSearchTool(catalogue_provider=crashing_provider)
        res = tool.search("Paracetamol")
        assert res.status == "error"
        assert "Error accessing medicine catalogue" in res.message


class TestPharmacySearchTool:
    """Tests ensuring pharmacy tool does not fabricate fake stores or locations."""

    def test_default_tool_returns_honest_unavailable_in_phase_5(self, default_pharmacy_tool: PharmacySearchTool):
        res = default_pharmacy_tool.search_pharmacies(query="Downtown")
        assert res.status == "unavailable"
        assert len(res.data) == 0
        assert "phase 6" in res.message.lower()

    def test_custom_pharmacy_provider(self):
        mock_pharmacies = [{"id": "p-01", "name": "Apollo Chemist"}]
        tool = PharmacySearchTool(pharmacy_provider=lambda **kwargs: mock_pharmacies)
        res = tool.search_pharmacies(query="Apollo")
        assert res.status == "success"
        assert len(res.data) == 1
        assert res.data[0]["name"] == "Apollo Chemist"
