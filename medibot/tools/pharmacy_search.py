"""
Pharmacy search tool interface and adapter for MediBot.

Encapsulates pharmacy directory lookup contracts. Explicitly returns unavailable
status when live backend directory services are not yet connected (Phase 6),
preventing the fabrication of fictitious establishments or stock data.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from medibot.tools.interfaces import ToolResult


class PharmacySearchTool:
    """
    Pharmacy directory search adapter for MediBot.

    Accepts an injectable provider for live pharmacy listings. When no provider
    is configured (prior to Phase 6 Search Integration), returns an explicit,
    truthful 'unavailable' result without fabricating fake stores or coordinates.
    """

    def __init__(
        self,
        pharmacy_provider: Optional[Callable[..., List[Dict[str, Any]]]] = None,
    ) -> None:
        self._provider = pharmacy_provider

    def search_pharmacies(
        self,
        query: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        max_radius_km: Optional[float] = None,
        limit: Optional[int] = 5,
    ) -> ToolResult:
        """
        Search verified pharmacy establishments.

        Args:
            query: Pharmacy name or locality query.
            lat: User latitude.
            lon: User longitude.
            max_radius_km: Optional search radius in kilometres.
            limit: Maximum pharmacies to return.

        Returns:
            ToolResult dataclass.
        """
        if self._provider is None:
            return ToolResult(
                status="unavailable",
                data=[],
                message=(
                    "Pharmacy directory search is scheduled for full integration in Phase 6. "
                    "Live pharmacy listings and location-based mapping are not yet connected in this assistant release."
                ),
                metadata={"phase": "Phase 5 Development"},
            )

        try:
            results = self._provider(
                query=query,
                lat=lat,
                lon=lon,
                max_radius_km=max_radius_km,
                limit=limit,
            )
            if not results:
                return ToolResult(
                    status="no_results",
                    data=[],
                    message="No matching pharmacies found in the directory for the specified criteria.",
                )
            return ToolResult(
                status="success",
                data=results,
                message=f"Found {len(results)} matching pharmacy establishment(s).",
            )
        except Exception as exc:
            return ToolResult(
                status="error",
                data=[],
                message=f"Error accessing pharmacy directory service: {str(exc)}",
            )
