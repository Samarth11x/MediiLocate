"""
Unit tests for medicine query and catalogue normalization.
"""

import pytest
from core_intelligence.search_engine.normalization import (
    normalize_text,
    normalize_strength,
    normalize_query,
    tokenize,
    extract_strength_and_form,
)


class TestTextNormalization:
    """Tests for basic text normalization."""

    def test_case_folding_and_whitespace(self):
        assert normalize_text("  PARACETAMOL   ") == "paracetamol"
        assert normalize_text("Amoxicillin   500mg") == "amoxicillin 500mg"
        assert normalize_text("  DOLO   650   ") == "dolo 650"

    def test_unicode_normalization(self):
        # Accented characters
        assert normalize_text("café medicine") == "café medicine"
        # Full-width characters
        assert normalize_text("Ａｍｏｘｉｃｉｌｌｉｎ") == "amoxicillin"
        # Micro sign to mcg
        assert normalize_text("10µg") == "10mcg"

    def test_punctuation_handling(self):
        # Disruptive punctuation stripped
        assert normalize_text("Crocin (Paracetamol)!") == "crocin paracetamol"
        assert normalize_text("[Augmentin] - 625 Duo?") == "augmentin 625 duo"
        # Medically meaningful characters preserved
        assert normalize_text("0.5% ointment") == "0.5% ointment"
        assert normalize_text("co-amoxiclav") == "co-amoxiclav"
        assert normalize_text("mg/ml") == "mg / ml"

    def test_empty_and_invalid_inputs(self):
        assert normalize_text("") == ""
        assert normalize_text("   ") == ""
        assert normalize_text(None) == ""
        assert normalize_text(123) == ""  # type: ignore


class TestStrengthNormalization:
    """Tests for strength unit standardizations."""

    def test_standard_units(self):
        assert normalize_strength("500mg") == "500 mg"
        assert normalize_strength("500 MG") == "500 mg"
        assert normalize_strength("500  mg") == "500 mg"
        assert normalize_strength("250mcg") == "250 mcg"
        assert normalize_strength("10ml") == "10 ml"
        assert normalize_strength("5g") == "5 g"
        assert normalize_strength("0.5%") == "0.5 %"
        assert normalize_strength("100iu") == "100 iu"

    def test_concentration_slashes(self):
        assert normalize_strength("250mg/5ml") == "250 mg / 5 ml"
        assert normalize_strength("125 mg / 5 ml") == "125 mg / 5 ml"
        assert normalize_strength("10mg/ml") == "10 mg / 1 ml" or normalize_strength("10mg/ml") == "10 mg / ml"

    def test_empty_strength(self):
        assert normalize_strength("") == ""
        assert normalize_strength(None) == ""


class TestQueryNormalization:
    """Tests for user query normalization."""

    def test_user_query_examples(self):
        assert normalize_query("  PARACETAMOL  500 MG  ") == "paracetamol 500 mg"
        assert normalize_query("paracetamol 500mg") == "paracetamol 500 mg"
        assert normalize_query("Dolo (650mg) Tablet") == "dolo 650 mg tablet"
        assert normalize_query("Augmentin-625 Duo") == "augmentin-625 duo" or "augmentin 625 duo" in normalize_query("Augmentin-625 Duo")

    def test_empty_query(self):
        assert normalize_query("") == ""
        assert normalize_query("   ") == ""
        assert normalize_query(None) == ""


class TestTokenization:
    """Tests for tokenizing normalized queries."""

    def test_tokenize_standard(self):
        tokens = tokenize("paracetamol 500mg tablet")
        assert tokens == ["paracetamol", "500", "mg", "tablet"]

    def test_tokenize_empty(self):
        assert tokenize("") == []
        assert tokenize("   ") == []
        assert tokenize(None) == []


class TestStrengthAndFormExtraction:
    """Tests for identifying explicit dosage and form in search queries."""

    def test_extract_both(self):
        strength, form = extract_strength_and_form("paracetamol 500mg tablet")
        assert strength == "500 mg"
        assert form == "tablet"

    def test_extract_concentration_and_syrup(self):
        strength, form = extract_strength_and_form("calpol 250mg/5ml syrup")
        assert strength == "250 mg / 5 ml"
        assert form == "syrup"

    def test_extract_form_only(self):
        strength, form = extract_strength_and_form("amoxicillin capsules")
        assert strength is None
        assert form == "capsule"

    def test_extract_strength_only(self):
        strength, form = extract_strength_and_form("dolo 650mg")
        assert strength == "650 mg"
        assert form is None

    def test_extract_none(self):
        strength, form = extract_strength_and_form("ibuprofen")
        assert strength is None
        assert form is None
