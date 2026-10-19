"""
Unit tests for MediBot intent classification.
"""

import pytest
from medibot.intents.classifier import classify_intent
from medibot.intents.patterns import IntentType


class TestIntentClassification:
    """Tests covering all supported intent categories and extraction logic."""

    def test_greeting_intent(self):
        for phrase in ["Hi", "Hello", "Hey", "Hello MediBot", "Good morning", "Hey there"]:
            res = classify_intent(phrase)
            assert res.intent == IntentType.GREETING
            assert res.confidence >= 0.90

    def test_how_it_works_intent(self):
        for phrase in [
            "How does MediLocate work?",
            "What is MediLocate?",
            "Tell me about MediLocate",
            "How does this platform work",
        ]:
            res = classify_intent(phrase)
            assert res.intent == IntentType.HOW_IT_WORKS

    def test_pharmacy_onboarding_intent(self):
        for phrase in [
            "How can my pharmacy join?",
            "How does a pharmacy register on MediLocate?",
            "Partner with MediLocate",
            "Pharmacy onboarding process",
        ]:
            res = classify_intent(phrase)
            assert res.intent == IntentType.PHARMACY_ONBOARDING

    def test_availability_help_intent(self):
        for phrase in [
            "What does low stock mean?",
            "What is low stock status?",
            "Explain availability status",
            "What does out of stock mean?",
        ]:
            res = classify_intent(phrase)
            assert res.intent == IntentType.AVAILABILITY_HELP

    def test_pharmacy_search_intent(self):
        for phrase in [
            "Find nearby pharmacies",
            "Pharmacies near me",
            "Chemists in my area",
            "Show me nearby medical stores",
        ]:
            res = classify_intent(phrase)
            assert res.intent == IntentType.PHARMACY_SEARCH

    def test_generic_medicine_search_without_entity(self):
        for phrase in ["Find a medicine", "Search for a medicine", "Lookup medicine"]:
            res = classify_intent(phrase)
            assert res.intent == IntentType.MEDICINE_SEARCH
            assert res.extracted_entity is None

    def test_specific_medicine_search_with_entity(self):
        res = classify_intent("Find Paracetamol 500mg")
        assert res.intent == IntentType.MEDICINE_SEARCH
        assert res.extracted_entity is not None
        assert "paracetamol" in res.extracted_entity.lower()

        res2 = classify_intent("Search for Amoxicillin capsules")
        assert res2.intent == IntentType.MEDICINE_SEARCH
        assert "amoxicillin" in res2.extracted_entity.lower()

        res3 = classify_intent("Where can I get Dolo 650?")
        assert res3.intent == IntentType.MEDICINE_SEARCH
        assert "dolo 650" in res3.extracted_entity.lower()

    def test_emergency_precedence_in_classifier(self):
        res = classify_intent("Find medicine for severe chest pain and heart attack")
        assert res.intent == IntentType.EMERGENCY_CONCERN
        assert res.confidence == 1.0

    def test_medical_advice_precedence_in_classifier(self):
        res = classify_intent("What medicine should I take for fever?")
        assert res.intent == IntentType.MEDICAL_ADVICE
        assert res.confidence == 1.0

    def test_unknown_intent_fallback(self):
        for phrase in [
            "What is the weather in Tokyo?",
            "Book a flight to Mumbai",
            "Tell me a joke",
            "abcdef 123456",
        ]:
            res = classify_intent(phrase)
            assert res.intent == IntentType.UNKNOWN
            assert res.confidence == 0.0
