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
