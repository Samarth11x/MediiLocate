"""
Medicine search tool adapter for MediBot.

Reuses Core Intelligence normalization and matching algorithms to perform
medicine discovery without duplicating logic or directly accessing the database.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from core_intelligence.search_engine.matching import search_medicines
from medibot.tools.interfaces import ToolResult


class MedicineSearchTool:
    """
    Adapter bridging MediBot to Core Intelligence search matching.

    Accepts an injectable catalogue provider (a callable returning a list of dicts,
    or a static list). If no provider is available or the catalogue is empty,
    returns an explicit, honest 'unavailable' status without fabricating records.
    """

    def __init__(
        self,
        catalogue_provider: Optional[Callable[[], List[Dict[str, Any]]] | List[Dict[str, Any]]] = None,
    ) -> None:
        self._provider = catalogue_provider

    def search(self, query: str, limit: Optional[int] = 5) -> ToolResult:
        """
        Execute medicine lookup against the provided catalogue using Core Intelligence.

        Args:
            query: User search string.
            limit: Maximum number of matches to return (default: 5).

        Returns:
            ToolResult dataclass.
        """
        if not query or not query.strip():
            return ToolResult(
                status="no_results",
                data=[],
                message="Please specify the medicine name or formulation to search.",
            )

        if self._provider is None:
            return ToolResult(
                status="unavailable",
                data=[],
                message="Medicine catalogue provider is not connected to MediBot.",
            )

        # Retrieve catalogue items safely
        try:
            if callable(self._provider):
                catalogue = self._provider()
            else:
                catalogue = self._provider
        except Exception as exc:
            return ToolResult(
                status="error",
                data=[],
                message=f"Error accessing medicine catalogue: {str(exc)}",
            )

        if not catalogue:
            return ToolResult(
                status="unavailable",
                data=[],
                message="Medicine catalogue is currently unpopulated in this development environment.",
            )

        # Execute Core Intelligence search matching with strict safeguards
        matches = search_medicines(query=query, medicines=catalogue, limit=limit)

        if not matches:
            return ToolResult(
                status="no_results",
                data=[],
                message=f"No medicines found matching '{query}'.",
            )

        return ToolResult(
            status="success",
            data=matches,
            message=f"Found {len(matches)} matching medicine(s) for '{query}'.",
        )
