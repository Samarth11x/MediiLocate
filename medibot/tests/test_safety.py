"""
Unit tests for MediBot medical safety guardrails and input validation.
"""

import pytest
from medibot.safety.input_validation import validate_input
from medibot.safety.emergency import check_emergency, EMERGENCY_RESPONSE_MESSAGE
from medibot.safety.safety_rules import check_medical_advice, MEDICAL_ADVICE_RESPONSE
from medibot.dialogue.manager import DialogueManager


class TestInputValidation:
    """Tests enforcing strict input sanitization and length bounds."""

    def test_valid_input(self):
        is_valid, cleaned, err = validate_input("  Find Paracetamol 500mg  ")
        assert is_valid is True
        assert cleaned == "Find Paracetamol 500mg"
        assert err is None

    def test_empty_string_rejected(self):
        is_valid, cleaned, err = validate_input("")
        assert is_valid is False
        assert cleaned is None
        assert err is not None
        assert err.status == "needs_clarification"

    def test_whitespace_only_rejected(self):
        is_valid, cleaned, err = validate_input("      ")
        assert is_valid is False
        assert err.status == "needs_clarification"

    def test_non_string_types_rejected(self):
        for bad_val in [None, 123, True, False, ["hello"], {"msg": "hi"}]:
            is_valid, cleaned, err = validate_input(bad_val)
            assert is_valid is False
            assert err is not None
            assert err.status == "error"

    def test_oversized_message_rejected(self):
        long_message = "a" * 501
        is_valid, cleaned, err = validate_input(long_message, max_length=500)
        assert is_valid is False
        assert err is not None
        assert err.status == "error"
        assert "exceeds" in err.message.lower()

    def test_boundary_length_allowed(self):
        boundary_message = "a" * 500
        is_valid, cleaned, err = validate_input(boundary_message, max_length=500)
        assert is_valid is True
        assert len(cleaned) == 500


class TestMedicalAdviceGuardrail:
    """Tests ensuring assistant never diagnoses, prescribes, or advises dosage alterations."""

    def test_treatment_recommendation_intercepted(self):
        resp = check_medical_advice("What should I take for severe headache?")
        assert resp is not None
        assert resp.intent == "MEDICAL_ADVICE"
        assert resp.status == "safety_response"
        assert resp.safety_category == "medical_advice"
        assert "consult a qualified medical doctor" in resp.message.lower()

    def test_prescribing_request_intercepted(self):
        resp = check_medical_advice("Can you recommend a medicine for fever?")
        assert resp is not None
        assert resp.intent == "MEDICAL_ADVICE"

    def test_dosage_recommendation_intercepted(self):
        resp = check_medical_advice("How much Paracetamol should I give my 5 year old?")
        assert resp is not None
        assert resp.intent == "MEDICAL_ADVICE"
        assert resp.status == "safety_response"

    def test_stopping_medication_intercepted(self):
        resp = check_medical_advice("Should I stop taking my blood pressure medicine?")
        assert resp is not None
        assert resp.intent == "MEDICAL_ADVICE"

    def test_diagnostics_intercepted(self):
        resp = check_medical_advice("Diagnose my skin rash")
        assert resp is not None
        assert resp.intent == "MEDICAL_ADVICE"

    def test_drug_interaction_intercepted(self):
        resp = check_medical_advice("Can I take Ibuprofen with Aspirin?")
        assert resp is not None
        assert resp.intent == "MEDICAL_ADVICE"

    def test_general_help_not_intercepted(self):
        # Product questions should NOT trigger medical advice
        assert check_medical_advice("What does low stock mean?") is None
        assert check_medical_advice("How does MediLocate work?") is None
        assert check_medical_advice("Find Paracetamol 500mg") is None


class TestEmergencyDetection:
    """Tests ensuring acute emergencies receive immediate life safety guidance."""

    def test_chest_pain_emergency(self):
        resp = check_emergency("I am having severe chest pain right now")
        assert resp is not None
        assert resp.intent == "EMERGENCY_CONCERN"
        assert resp.status == "safety_response"
        assert resp.safety_category == "emergency_concern"
        assert "112" in resp.message or "emergency" in resp.message.lower()

    def test_breathing_emergency(self):
        resp = check_emergency("My father cannot breathe and is choking")
        assert resp is not None
        assert resp.intent == "EMERGENCY_CONCERN"

    def test_overdose_emergency(self):
        resp = check_emergency("I accidentally took whole bottle of pills")
        assert resp is not None
        assert resp.intent == "EMERGENCY_CONCERN"

    def test_stroke_emergency(self):
        resp = check_emergency("Person collapsed with sudden face drooping and seizure")
        assert resp is not None
        assert resp.intent == "EMERGENCY_CONCERN"

    def test_non_emergency_query_passes(self):
        assert check_emergency("Where can I buy Paracetamol?") is None
        assert check_emergency("What are the pharmacy hours?") is None


class TestSafetyPrecedenceInDialogueManager:
    """Tests verifying safety checks take absolute priority over ordinary dialogue."""

    def test_emergency_preempts_medicine_search(self, test_dialogue_manager: DialogueManager):
        # Query contains both a medicine keyword and an emergency keyword
        resp = test_dialogue_manager.process_message("I took entire bottle of Paracetamol, find hospital")
        assert resp.intent == "EMERGENCY_CONCERN"
        assert resp.status == "safety_response"
        assert resp.safety_category == "emergency_concern"
        # Tool results must NOT be returned for emergencies
        assert len(resp.results) == 0

    def test_medical_advice_preempts_ordinary_search(self, test_dialogue_manager: DialogueManager):
        resp = test_dialogue_manager.process_message("What dose of Amoxicillin should I take for cough?")
        assert resp.intent == "MEDICAL_ADVICE"
        assert resp.status == "safety_response"
        assert resp.safety_category == "medical_advice"
        assert len(resp.results) == 0
