"""
Abstract tool interfaces and result dataclasses for MediBot.

Tools are injected into MediBot by backend services or test harnesses,
guaranteeing zero direct database or web framework coupling inside the assistant.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class ToolResult:
    """
    Standardized outcome returned by an injected tool.

    Attributes:
        status: 'success', 'no_results', 'unavailable', or 'error'.
        data: List of structured result dictionaries.
        message: Human-readable status or error explanation.
        metadata: Optional execution details or timestamps.
    """
    status: str  # 'success', 'no_results', 'unavailable', 'error'
    data: List[Dict[str, Any]] = field(default_factory=list)
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class MedicineSearchToolProtocol(Protocol):
    """Protocol for medicine catalogue lookup tools."""
    def search(self, query: str, limit: Optional[int] = 5) -> ToolResult:
        ...


@runtime_checkable
class PharmacySearchToolProtocol(Protocol):
    """Protocol for pharmacy location and directory tools."""
    def search_pharmacies(
        self,
        query: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        max_radius_km: Optional[float] = None,
        limit: Optional[int] = 5,
        medicine_name: Optional[str] = None,
        medicine_id: Optional[Any] = None,
    ) -> ToolResult:
        ...
