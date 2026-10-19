"""
Medicine search matching module.

Provides pure Python, deterministic medicine search with support for:
- Exact and partial generic name matching
- Exact and partial brand name matching
- Explicit search aliases matching
- Configurable difflib fuzzy matching
- Medication identity safeguards (strict strength and dosage form enforcement)
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from core_intelligence.search_engine.normalization import (
    normalize_query,
    normalize_strength,
    normalize_text,
    extract_strength_and_form,
    tokenize,
    DOSAGE_FORM_MAPPINGS,
)


@dataclass
class MedicineMatchResult:
    """
    Structured outcome of matching a medicine against a user query.
    """
    medicine: Dict[str, Any]
    match_score: float
    match_type: str  # 'exact_name', 'exact_alias', 'partial_name', 'partial_alias', 'fuzzy'
    matched_fields: List[str]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a plain dictionary."""
        return {
            "medicine": self.medicine,
            "match_score": round(self.match_score, 4),
            "match_type": self.match_type,
            "matched_fields": list(self.matched_fields),
            "explanation": self.explanation,
        }


def _calculate_fuzzy_score(query: str, target: str) -> float:
    """
    Calculate similarity ratio using standard library difflib.SequenceMatcher.
    """
    if not query or not target:
        return 0.0
    return difflib.SequenceMatcher(None, query, target).ratio()


def search_medicines(
    query: Optional[str],
    medicines: List[Dict[str, Any]],
    limit: Optional[int] = None,
    fuzzy_threshold: float = 0.70,
) -> List[Dict[str, Any]]:
    """
    Search a catalogue of medicines against a user query.

    Catalogue entries are neutral dictionaries with keys:
    - id: unique identifier
    - generic_name: chemical constituent name
    - brand_name: trade/commercial name
    - strength: formulation strength (optional)
    - dosage_form: formulation form (optional)
    - search_aliases: list of synonyms/common misspellings (optional)

    Medication Identity Safeguards:
    - If the user query specifies an explicit strength (e.g. '500 mg'), medicines
      with a conflicting explicit strength (e.g. '650 mg') are excluded.
    - If the user query specifies an explicit dosage form (e.g. 'syrup'), medicines
      with a conflicting explicit form (e.g. 'tablet') are excluded.

    Args:
        query: User search string.
        medicines: List of medicine catalogue dictionaries.
        limit: Optional maximum number of matches to return.
        fuzzy_threshold: Minimum difflib ratio to consider a fuzzy match (0.0 to 1.0).

    Returns:
        List of result dictionaries sorted deterministically by match_score descending,
        then brand_name alphabetical, then id.
    """
    normalized_q = normalize_query(query)
    if not normalized_q or not medicines:
        return []

    q_tokens = tokenize(normalized_q)
    explicit_strength, explicit_form = extract_strength_and_form(normalized_q)

    # Filter out strength and form tokens from query to get core medicine name tokens
    name_tokens = []
    skip_tokens = set()
    if explicit_strength:
        for st in explicit_strength.split():
            skip_tokens.add(st)
    if explicit_form:
        for form_word, canonical in DOSAGE_FORM_MAPPINGS.items():
            if canonical == explicit_form:
                skip_tokens.add(form_word)

    for tok in q_tokens:
        if tok not in skip_tokens:
            name_tokens.append(tok)

    core_name_query = " ".join(name_tokens) if name_tokens else normalized_q

    matches: List[MedicineMatchResult] = []

    for med in medicines:
        if not isinstance(med, dict):
            continue

        raw_generic = med.get("generic_name") or ""
        raw_brand = med.get("brand_name") or ""
        raw_strength = med.get("strength") or ""
        raw_form = med.get("dosage_form") or ""
        raw_aliases = med.get("search_aliases") or []

        norm_generic = normalize_text(raw_generic)
        norm_brand = normalize_text(raw_brand)
        norm_strength = normalize_strength(raw_strength)
        norm_form = normalize_text(raw_form)
        canonical_med_form = DOSAGE_FORM_MAPPINGS.get(norm_form, norm_form)

        # Safeguard 1: Explicit Strength Mismatch
        if explicit_strength and norm_strength:
            if explicit_strength != norm_strength:
                # User asked for explicit strength, but this medicine has a different strength
                continue

        # Safeguard 2: Explicit Dosage Form Mismatch
        if explicit_form and canonical_med_form:
            if explicit_form != canonical_med_form:
                # User asked for explicit form, but this medicine is a different form
                continue

        match_score = 0.0
        match_type = ""
        matched_fields: List[str] = []
        explanation_parts: List[str] = []

        # Check 1: Exact matches on generic or brand name
        if normalized_q == norm_generic or core_name_query == norm_generic:
            match_score = 1.0
            match_type = "exact_name"
            matched_fields.append("generic_name")
            explanation_parts.append(f"Exact match on generic name '{raw_generic}'")
        elif normalized_q == norm_brand or core_name_query == norm_brand:
            match_score = 1.0
            match_type = "exact_name"
            matched_fields.append("brand_name")
            explanation_parts.append(f"Exact match on brand name '{raw_brand}'")

        # Check 2: Exact matches on aliases
        if match_score == 0.0 and raw_aliases:
            for alias in raw_aliases:
                norm_alias = normalize_text(alias)
                if normalized_q == norm_alias or core_name_query == norm_alias:
                    match_score = 0.98
                    match_type = "exact_alias"
                    matched_fields.append("search_aliases")
                    explanation_parts.append(f"Exact match on search alias '{alias}'")
                    # Also record brand or generic if query is contained in them
                    if core_name_query and (core_name_query in norm_brand or norm_brand in core_name_query):
                        if "brand_name" not in matched_fields:
                            matched_fields.append("brand_name")
                    if core_name_query and (core_name_query in norm_generic or norm_generic in core_name_query):
                        if "generic_name" not in matched_fields:
                            matched_fields.append("generic_name")
                    break

        # Check 3: Partial substring matches (word-boundary or containment)
        if match_score == 0.0:
            generic_matched = (core_name_query and core_name_query in norm_generic) or (norm_generic and norm_generic in core_name_query)
            brand_matched = (core_name_query and core_name_query in norm_brand) or (norm_brand and norm_brand in core_name_query)

            if brand_matched and generic_matched:
                match_score = 0.95
                match_type = "partial_name"
                matched_fields.extend(["brand_name", "generic_name"])
                explanation_parts.append(f"Matched brand '{raw_brand}' and generic '{raw_generic}'")
            elif brand_matched:
                match_score = 0.92
                match_type = "partial_name"
                matched_fields.append("brand_name")
                explanation_parts.append(f"Partial match on brand name '{raw_brand}'")
            elif generic_matched:
                match_score = 0.90
                match_type = "partial_name"
                matched_fields.append("generic_name")
                explanation_parts.append(f"Partial match on generic name '{raw_generic}'")

        # Check 4: Partial matches on aliases
        if match_score == 0.0 and raw_aliases:
            for alias in raw_aliases:
                norm_alias = normalize_text(alias)
                if (core_name_query and core_name_query in norm_alias) or (norm_alias and norm_alias in core_name_query):
                    match_score = 0.85
                    match_type = "partial_alias"
                    matched_fields.append("search_aliases")
                    explanation_parts.append(f"Partial match on alias '{alias}'")
                    break

        # Check 5: Fuzzy matching with SequenceMatcher (supporting signal)
        if match_score == 0.0 and core_name_query:
            best_fuzzy_ratio = 0.0
            best_fuzzy_field = ""
            best_fuzzy_val = ""

            # Check generic name tokens
            for g_tok in norm_generic.split():
                ratio = _calculate_fuzzy_score(core_name_query, g_tok)
                if ratio > best_fuzzy_ratio:
                    best_fuzzy_ratio = ratio
                    best_fuzzy_field = "generic_name"
                    best_fuzzy_val = raw_generic

            # Check brand name tokens
            for b_tok in norm_brand.split():
                ratio = _calculate_fuzzy_score(core_name_query, b_tok)
                if ratio > best_fuzzy_ratio:
                    best_fuzzy_ratio = ratio
                    best_fuzzy_field = "brand_name"
                    best_fuzzy_val = raw_brand

            # Whole string similarity
            ratio_g = _calculate_fuzzy_score(core_name_query, norm_generic)
            if ratio_g > best_fuzzy_ratio:
                best_fuzzy_ratio = ratio_g
                best_fuzzy_field = "generic_name"
                best_fuzzy_val = raw_generic

            ratio_b = _calculate_fuzzy_score(core_name_query, norm_brand)
            if ratio_b > best_fuzzy_ratio:
                best_fuzzy_ratio = ratio_b
                best_fuzzy_field = "brand_name"
                best_fuzzy_val = raw_brand

            if best_fuzzy_ratio >= fuzzy_threshold:
                # Map fuzzy ratio [threshold, 1.0] to score range [0.70, 0.84]
                normalized_ratio = (best_fuzzy_ratio - fuzzy_threshold) / (1.0 - fuzzy_threshold) if fuzzy_threshold < 1.0 else 0.5
                match_score = 0.70 + (0.14 * normalized_ratio)
                match_type = "fuzzy"
                matched_fields.append(best_fuzzy_field)
                pct = int(best_fuzzy_ratio * 100)
                explanation_parts.append(f"Fuzzy match ({pct}% similarity) on {best_fuzzy_field} '{best_fuzzy_val}'")

        # If a match was found, record any matching strength or form in matched_fields
        if match_score > 0.0:
            if explicit_strength and norm_strength and explicit_strength == norm_strength:
                matched_fields.append("strength")
                explanation_parts.append(f"Matched strength '{raw_strength}'")
            if explicit_form and canonical_med_form and explicit_form == canonical_med_form:
                matched_fields.append("dosage_form")
                explanation_parts.append(f"Matched formulation '{raw_form}'")

            matches.append(
                MedicineMatchResult(
                    medicine=med,
                    match_score=match_score,
                    match_type=match_type,
                    matched_fields=matched_fields,
                    explanation="; ".join(explanation_parts),
                )
            )

    # Deterministic sort: score DESC, brand_name ASC, id ASC
    matches.sort(
        key=lambda r: (
            -r.match_score,
            (r.medicine.get("brand_name") or "").lower(),
            str(r.medicine.get("id") or ""),
        )
    )

    if limit is not None and limit > 0:
        matches = matches[:limit]

    return [m.to_dict() for m in matches]
