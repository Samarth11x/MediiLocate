"""
Medicine search normalization module.

Provides deterministic, standard-library text and strength normalization for
pharmaceutical queries and catalogue records. Preserves medically significant
numeric values, strength units, and active ingredient distinctions.
"""

from __future__ import annotations

import html
import re
import unicodedata
from typing import Optional, Tuple, List, Set

# Recognized strength units in lower-case
STRENGTH_UNITS: Set[str] = {
    "mg",
    "mcg",
    "ug",
    "µg",
    "g",
    "kg",
    "ml",
    "l",
    "iu",
    "meq",
    "mmol",
    "%",
    "w/v",
    "w/w",
}

# Regex to match numeric values attached to units (e.g., '500mg', '0.5%')
_STRENGTH_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mcg|µg|ug|g|kg|ml|l|iu|meq|mmol|%)(?=\s|$|[^\w])",
    re.IGNORECASE,
)

# Regex to standardize slashes in concentrations (e.g. '500 mg/5 ml' -> '500 mg / 5 ml')
_SLASH_PATTERN = re.compile(r"\s*/\s*")

# Punctuation to strip/replace with whitespace (excluding medically meaningful characters like decimals, hyphens, plus, percent)
_DISRUPTIVE_PUNCT_PATTERN = re.compile(r"[()[\]{}<>\"'?!:;,~*#@$^&=|\\`]")

# Canonical dosage form mappings
DOSAGE_FORM_MAPPINGS = {
    "tablet": "tablet",
    "tablets": "tablet",
    "tab": "tablet",
    "tabs": "tablet",
    "capsule": "capsule",
    "capsules": "capsule",
    "cap": "capsule",
    "caps": "capsule",
    "syrup": "syrup",
    "suspension": "suspension",
    "injection": "injection",
    "injectable": "injection",
    "ampoule": "injection",
    "vial": "injection",
    "cream": "cream",
    "ointment": "ointment",
    "gel": "gel",
    "drops": "drops",
    "inhaler": "inhaler",
    "spray": "spray",
    "patch": "patch",
    "solution": "solution",
    "suppository": "suppository",
    "lotion": "lotion",
    "powder": "powder",
}


def normalize_text(text: Optional[str]) -> str:
    """
    Standardize text by normalizing Unicode, folding case, removing
    disruptive punctuation, and collapsing repeated whitespace.

    Args:
        text: Input string, or None.

    Returns:
        Clean normalized lowercase string, or empty string if input is None/empty.
    """
    if not text or not isinstance(text, str):
        return ""

    # Unescape any unintended HTML entities (e.g. &#x35; -> '5', &#x31; -> '1')
    raw_clean = html.unescape(text)

    # Normalize Unicode (NFKC handles full-width characters, micro signs, etc.)
    normalized = unicodedata.normalize("NFKC", raw_clean)

    # Word-boundary replacement of micro symbol µg or standalone ug to standard mcg
    normalized = re.sub(r"(?<=\d)\s*(?:µg|ug)(?=\s|$|[^\w])", "mcg", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\b(?:µg|ug)\b", "mcg", normalized, flags=re.IGNORECASE)

    # Lowercase
    normalized = normalized.lower()

    # Replace disruptive punctuation with spaces
    normalized = _DISRUPTIVE_PUNCT_PATTERN.sub(" ", normalized)

    # Standardize slash spacing (e.g., 'mg/ml' -> 'mg / ml')
    normalized = _SLASH_PATTERN.sub(" / ", normalized)

    # Standardize standalone hyphens, keeping intra-word hyphens (e.g., 'co-amoxiclav')
    normalized = re.sub(r"(?<![a-z0-9])-(?![a-z0-9])", " ", normalized)

    # Collapse repeated whitespace
    return " ".join(normalized.split())


def normalize_strength(strength: Optional[str]) -> str:
    """
    Normalize strength strings into standardized '<number> <unit>' representations.

    Examples:
        '500MG' -> '500 mg'
        '0.5 %' -> '0.5 %'
        '250mg/5ml' -> '250 mg / 5 ml'
        '10 mcg' -> '10 mcg'

    Args:
        strength: Raw strength string.

    Returns:
        Standardized strength string, or empty string if None/empty.
    """
    if not strength or not isinstance(strength, str):
        return ""

    text = normalize_text(strength)

    # Separate number from unit consistently with a single space
    def _unit_repl(match: re.Match) -> str:
        num = match.group(1)
        unit = match.group(2).lower()
        if unit in ("µg", "ug"):
            unit = "mcg"
        return f"{num} {unit}"

    standardized = _STRENGTH_PATTERN.sub(_unit_repl, text)
    # Ensure slash spacing is uniform
    standardized = _SLASH_PATTERN.sub(" / ", standardized)
    return " ".join(standardized.split())


def normalize_query(query: Optional[str]) -> str:
    """
    Perform comprehensive normalization of a user search query.

    Handles:
    - Unicode & case normalization
    - Punctuation standardization
    - Strength unit spacing ('500mg' -> '500 mg')
    - Whitespace collapsing

    Args:
        query: User input medicine search query.

    Returns:
        Normalized query string.
    """
    if not query or not isinstance(query, str):
        return ""

    cleaned = normalize_text(query)
    # Apply strength unit normalization on query tokens
    return normalize_strength(cleaned)


def tokenize(text: Optional[str]) -> List[str]:
    """
    Split normalized text into meaningful tokens.

    Args:
        text: Input string.

    Returns:
        List of non-empty tokens.
    """
    normalized = normalize_query(text)
    if not normalized:
        return []
    return normalized.split()


def extract_strength_and_form(query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract any explicitly stated strength and dosage form from a query.

    This enables strict attribute-matching safeguards to prevent silent
    substitution of different dosages (e.g. 500mg vs 650mg) or formulations
    (e.g. tablet vs syrup).

    Args:
        query: User query string.

    Returns:
        Tuple of (explicit_strength, canonical_dosage_form), each Optional[str].
    """
    if not query or not isinstance(query, str):
        return None, None

    normalized = normalize_query(query)
    tokens = normalized.split()

    # Search for strength patterns (e.g. '500 mg', '250 mg / 5 ml', '0.5 %')
    strengths_found = []
    # Match complex concentrations first (e.g. '250 mg / 5 ml')
    complex_match = re.search(
        r"(\d+(?:\.\d+)?\s*(?:mg|mcg|g|kg|ml|l|iu|meq|%)\s*/\s*\d+(?:\.\d+)?\s*(?:mg|mcg|g|kg|ml|l|iu|meq|%))",
        normalized,
    )
    if complex_match:
        strengths_found.append(normalize_strength(complex_match.group(1)))
    else:
        # Match single strengths
        for match in _STRENGTH_PATTERN.finditer(normalized):
            strengths_found.append(f"{match.group(1)} {match.group(2).lower()}")

    extracted_strength = strengths_found[0] if strengths_found else None

    # Search for dosage form
    extracted_form = None
    for token in tokens:
        if token in DOSAGE_FORM_MAPPINGS:
            extracted_form = DOSAGE_FORM_MAPPINGS[token]
            break

    return extracted_strength, extracted_form
