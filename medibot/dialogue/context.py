"""
MediBot conversation context and response contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class ConversationContext:
    """
    Lightweight, client-supplied conversation context.

    Keeps state non-sensitive and strictly whitelisted to prevent untrusted
    state tampering. Not persisted to any database.
    """
    last_intent: Optional[str] = None
    searched_medicine: Optional[str] = None
    searched_medicine_id: Optional[str] = None
    step: Optional[str] = None
    user_lat: Optional[float] = None
    user_lon: Optional[float] = None

    WHITELISTED_KEYS = {
        "last_intent",
        "searched_medicine",
        "searched_medicine_id",
        "step",
        "user_lat",
        "user_lon",
    }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> ConversationContext:
        """Create context instance from client dictionary, discarding unknown keys."""
        if not data or not isinstance(data, dict):
            return cls()

        clean_kwargs: Dict[str, Any] = {}
        for k, v in data.items():
            if k in cls.WHITELISTED_KEYS and v is not None:
                if k in {"user_lat", "user_lon"}:
                    try:
                        clean_kwargs[k] = float(v)
                    except (ValueError, TypeError):
                        pass
                else:
                    clean_kwargs[k] = str(v)[:100]  # Cap string lengths to prevent memory injection
        return cls(**clean_kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to safe dictionary."""
        return {
            k: v for k, v in asdict(self).items() if v is not None
        }


@dataclass
class MediBotResponse:
    """
    Predictable, documented MediBot response payload.

    Attributes:
        message: Primary user-facing text response.
        intent: Recognized intent identifier (e.g., 'GREETING', 'MEDICINE_SEARCH').
        status: Response status code:
                'success', 'needs_clarification', 'no_results', 'unavailable', 'safety_response', 'error'.
        suggestions: Optional quick-reply follow-up action prompts.
        results: Optional list of matching medicine/catalogue entries.
        demo_notice: Boolean indicating whether responses rely on fictional demonstration data.
        safety_category: Optional non-diagnostic safety classification:
                         'emergency_concern', 'medical_advice', 'input_validation', or None.
        context: Updated non-sensitive conversation context.
    """
    message: str
    intent: str
    status: str
    suggestions: List[str] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    demo_notice: bool = True
    safety_category: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize response to JSON-safe dictionary."""
        return {
            "message": self.message,
            "intent": self.intent,
            "status": self.status,
            "suggestions": list(self.suggestions),
            "results": list(self.results),
            "demo_notice": self.demo_notice,
            "safety_category": self.safety_category,
            "context": self.context or {},
        }
