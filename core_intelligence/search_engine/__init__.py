"""
Medicine search engine subpackage: query normalization, tokenization, and matching.
"""

from core_intelligence.search_engine.normalization import (
    normalize_text,
    normalize_strength,
    normalize_query,
    tokenize,
    extract_strength_and_form,
)
from core_intelligence.search_engine.matching import (
    search_medicines,
    MedicineMatchResult,
)

__all__ = [
    "normalize_text",
    "normalize_strength",
    "normalize_query",
    "tokenize",
    "extract_strength_and_form",
    "search_medicines",
    "MedicineMatchResult",
]
