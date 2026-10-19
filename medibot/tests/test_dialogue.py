"""
Unit tests for MediBot dialogue management and multi-turn workflows.
"""

import pytest
from medibot.dialogue.manager import DialogueManager
from medibot.intents.patterns import IntentType


class TestDialogueManager:
    """Tests covering end-to-end dialogue workflows, clarification, and response structure."""

    def test_greeting_workflow(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("Hello MediBot")
        assert resp.intent == IntentType.GREETING
        assert resp.status == "success"
        assert "MediBot" in resp.message
        assert len(resp.suggestions) > 0
        assert resp.demo_notice is True
        assert resp.safety_category is None

    def test_how_it_works_workflow(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("How does MediLocate work?")
        assert resp.intent == IntentType.HOW_IT_WORKS
        assert resp.status == "success"
        assert "Search" in resp.message
        assert "Locate" in resp.message
        assert "Verify" in resp.message

    def test_pharmacy_onboarding_workflow(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("How can my pharmacy join?")
        assert resp.intent == IntentType.PHARMACY_ONBOARDING
        assert resp.status == "success"
        assert "partner" in resp.message.lower() or "pharmacies" in resp.message.lower()

    def test_availability_help_workflow(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("What does low stock mean?")
        assert resp.intent == IntentType.AVAILABILITY_HELP
        assert resp.status == "success"
        assert "LOW STOCK" in resp.message
        assert "10 units" in resp.message

    def test_medicine_search_direct(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("Find Crocin 500")
        assert resp.intent == IntentType.MEDICINE_SEARCH
        assert resp.status == "success"
        assert len(resp.results) >= 1
        assert "Crocin 500" in resp.message

    def test_medicine_search_needs_clarification_then_resolution(self, test_dialogue_manager: DialogueManager):
        # Turn 1: User asks generic "Find a medicine"
        turn1 = test_dialogue_manager.process_message("Find a medicine")
        assert turn1.intent == IntentType.MEDICINE_SEARCH
        assert turn1.status == "needs_clarification"
        assert "Which medicine" in turn1.message
        assert turn1.context.get("step") == "awaiting_medicine_name"

        # Turn 2: User provides the specific medicine name with previous context
        turn2 = test_dialogue_manager.process_message("Crocin 500", context=turn1.context)
        assert turn2.intent == IntentType.MEDICINE_SEARCH
        assert turn2.status == "success"
        assert len(turn2.results) >= 1
        assert "Crocin 500" in turn2.message

    def test_medicine_search_no_results(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("Find UnknownDrugXYZ")
        assert resp.intent == IntentType.MEDICINE_SEARCH
        assert resp.status == "no_results"
        assert len(resp.results) == 0
        assert "couldn't find any medicines" in resp.message.lower()

    def test_unsupported_question(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("Can you play some music?")
        assert resp.intent == IntentType.UNKNOWN
        assert resp.status == "needs_clarification"
        assert len(resp.suggestions) > 0

    def test_response_to_dict_schema(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("Hi")
        resp_dict = resp.to_dict()

        expected_keys = {
            "message",
            "intent",
            "status",
            "suggestions",
            "results",
            "demo_notice",
            "safety_category",
            "context",
        }
        assert set(resp_dict.keys()) == expected_keys
        assert isinstance(resp_dict["suggestions"], list)
        assert isinstance(resp_dict["results"], list)
        assert isinstance(resp_dict["context"], dict)

    def test_pharmacy_search_workflow_with_context(self, connected_medicine_tool):
        """Verify pharmacy search preserves medicine context and formats results."""
        from medibot.tools.pharmacy_search import PharmacySearchTool

        synthetic_pharmacy_data = [
            {
                "id": 1,
                "pharmacy": {
                    "id": 1,
                    "name": "CarePoint Pharmacy",
                    "area": "Koramangala",
                    "city": "Bengaluru",
                    "is_demo": True,
                },
                "quantity": 25,
                "stock_status": "AVAILABLE",
                "stock_status_label": "Available",
                "price": 30.5,
                "distance_km": None,
                "is_demo": True,
            }
        ]
        pharmacy_tool = PharmacySearchTool(pharmacy_provider=lambda **kwargs: synthetic_pharmacy_data)
        dm = DialogueManager(medicine_tool=connected_medicine_tool, pharmacy_tool=pharmacy_tool)

        # Turn 1: Search medicine
        turn1 = dm.process_message("Find Crocin 500")
        assert turn1.status == "success"
        assert turn1.context.get("searched_medicine") is not None

        # Turn 2: Follow up with Find nearby pharmacies
        turn2 = dm.process_message("Find nearby pharmacies", context=turn1.context)
        assert turn2.intent == IntentType.PHARMACY_SEARCH
        assert turn2.status == "success"
        assert len(turn2.results) == 1
        assert "CarePoint Pharmacy" in turn2.message
        assert "Available" in turn2.message
        assert "with inventory records for" in turn2.message
        assert "Availability varies by pharmacy" in turn2.message
        assert "Device location was not shared" in turn2.message

    def test_response_formatting_hex_entities_decoded(self):
        """Verify HTML/hex entities (&#x35;, &#x31;) are cleanly decoded in responses."""
        from medibot.dialogue.responses import (
            format_medicine_search_response,
            format_pharmacy_search_response,
        )

        matches = [
            {
                "medicine": {
                    "brand_name": "Crocin",
                    "generic_name": "Paracetamol",
                    "strength": "&#x35;00mg",
                    "dosage_form": "Tablet",
                }
            }
        ]
        med_text = format_medicine_search_response("Paracetamol &#x35;00mg", matches)
        assert "&#x35;" not in med_text
        assert "500mg" in med_text

        pharm_results = [
            {
                "pharmacy": {
                    "name": "Med&#x31; Plus",
                    "area": "Area &#x35;",
                    "city": "City",
                },
                "stock_status": "AVAILABLE",
                "stock_status_label": "Available",
            }
        ]
        pharm_text = format_pharmacy_search_response(pharm_results, medicine_name="Paracetamol &#x35;00mg")
        assert "&#x31;" not in pharm_text
        assert "&#x35;" not in pharm_text
        assert "Med1 Plus" in pharm_text
        assert "Area 5" in pharm_text

    def test_pharmacy_response_wording_distinguishes_inventory_from_availability(self):
        """
        REGRESSION TEST FOR RESPONSE COPY:
        Verify response copy accurately describes inventory records without
        implying that every pharmacy has stock or that OUT_OF_STOCK / UNKNOWN means available.
        """
        from medibot.dialogue.responses import format_pharmacy_search_response

        results = [
            {
                "pharmacy": {"name": "Apollo Chemist", "area": "Jayanagar", "city": "Bengaluru", "is_demo": True},
                "quantity": 0,
                "stock_status": "OUT_OF_STOCK",
                "stock_status_label": "Out of Stock",
                "price": 29.00,
                "distance_km": None,
                "is_demo": True,
            },
            {
                "pharmacy": {"name": "GreenCross Meds", "area": "Whitefield", "city": "Bengaluru", "is_demo": True},
                "quantity": None,
                "stock_status": "UNKNOWN",
                "stock_status_label": "Availability Unknown",
                "price": 31.00,
                "distance_km": None,
                "is_demo": True,
            },
            {
                "pharmacy": {"name": "CarePoint Pharmacy", "area": "Koramangala", "city": "Bengaluru", "is_demo": True},
                "quantity": 45,
                "stock_status": "AVAILABLE",
                "stock_status_label": "Available",
                "price": 30.50,
                "distance_km": None,
                "is_demo": True,
            },
            {
                "pharmacy": {"name": "Metro Chemist", "area": "Indiranagar", "city": "Bengaluru", "is_demo": True},
                "quantity": 5,
                "stock_status": "LOW_STOCK",
                "stock_status_label": "Low Stock",
                "price": 32.00,
                "distance_km": None,
                "is_demo": True,
            },
        ]
        text = format_pharmacy_search_response(results, medicine_name="Paracetamol 500mg")

        # 1. Header wording check: accurately describes inventory records without implying universal stock
        assert "I found 4 verified pharmacies with inventory records for 'Paracetamol 500mg'." in text
        assert "Availability varies by pharmacy; please note the stock status shown for each listing." in text
        assert "stocking" not in text.lower()

        # 2. Stock statuses preserved and accurately described
        assert "Stock: Out of Stock (0 available)" in text
        assert "Stock: Availability Unknown (count unconfirmed)" in text
        assert "Stock: Available (45 in stock)" in text
        assert "Stock: Low Stock (5 left in stock)" in text

        # 3. Demo disclaimer check
        assert "Demonstration Notice: Displayed pharmacies and inventory records are simulated demo data." in text
