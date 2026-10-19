"""
Inventory freshness and presentation status evaluation.

Evaluates how recently an inventory record was updated, distinguishing
fresh, stale, missing, and future/invalid timestamps independently of reported stock.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, Any

from core_intelligence.availability.rules import (
    AvailabilityStatus,
    AvailabilityConfig,
    DEFAULT_AVAILABILITY_CONFIG,
    classify_availability,
    validate_quantity,
)


class FreshnessStatus:
    """Freshness classification categories."""
    FRESH = "FRESH"
    STALE = "STALE"
    MISSING = "MISSING"
    FUTURE_INVALID = "FUTURE_INVALID"


class DisplayStatus:
    """Presentation availability status shown to users."""
    AVAILABLE = "AVAILABLE"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    UNKNOWN = "UNKNOWN"
    OUTDATED = "OUTDATED"


# Default freshness window: 24 hours
DEFAULT_FRESHNESS_THRESHOLD = timedelta(hours=24)

# Future tolerance for small clock drifts between servers (e.g., 60 seconds)
FUTURE_CLOCK_DRIFT_TOLERANCE = timedelta(seconds=60)


@dataclass(frozen=True)
class FreshnessResult:
    """
    Structured outcome of inventory freshness evaluation.
    """
    freshness_status: str  # FRESH, STALE, MISSING, FUTURE_INVALID
    age_seconds: Optional[float]
    is_current: bool  # True only if FRESH
    display_status: str  # CONFIRMED, OUTDATED, UNCONFIRMED
    reason: str


@dataclass(frozen=True)
class DisplayAvailabilityResult:
    """
    Combined outcome of reported availability and freshness for UI/presentation.
    """
    reported_status: str  # AVAILABLE, LOW_STOCK, OUT_OF_STOCK, UNKNOWN
    freshness_status: str  # FRESH, STALE, MISSING, FUTURE_INVALID
    display_status: str  # AVAILABLE, LOW_STOCK, OUT_OF_STOCK, UNKNOWN, OUTDATED
    is_confirmed: bool  # True only if reported quantity is known and freshness is FRESH
    age_seconds: Optional[float]
    reason: str


def _normalize_datetime(dt: datetime) -> datetime:
    """
    Ensure a datetime is timezone-aware in UTC.
    If naive, assume UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def evaluate_freshness(
    last_updated: Optional[datetime],
    current_time: Optional[datetime] = None,
    threshold: timedelta = DEFAULT_FRESHNESS_THRESHOLD,
) -> FreshnessResult:
    """
    Evaluate the freshness of an inventory record against a reference time.

    Args:
        last_updated: Datetime the inventory was last modified.
        current_time: Current time for evaluation (explicitly injectable for tests).
                      Defaults to datetime.now(timezone.utc) if None.
        threshold: Timedelta threshold after which records are considered STALE.

    Returns:
        FreshnessResult dataclass.
    """
    if last_updated is None:
        return FreshnessResult(
            freshness_status=FreshnessStatus.MISSING,
            age_seconds=None,
            is_current=False,
            display_status="UNCONFIRMED",
            reason="Inventory timestamp is missing",
        )

    if not isinstance(last_updated, datetime):
        return FreshnessResult(
            freshness_status=FreshnessStatus.FUTURE_INVALID,
            age_seconds=None,
            is_current=False,
            display_status="UNCONFIRMED",
            reason="Invalid timestamp format; datetime instance required",
        )

    # Reference time
    ref_time = current_time if current_time is not None else datetime.now(timezone.utc)
    norm_last_updated = _normalize_datetime(last_updated)
    norm_current = _normalize_datetime(ref_time)

    # Check for future timestamp (beyond drift tolerance)
    if norm_last_updated > (norm_current + FUTURE_CLOCK_DRIFT_TOLERANCE):
        return FreshnessResult(
            freshness_status=FreshnessStatus.FUTURE_INVALID,
            age_seconds=None,
            is_current=False,
            display_status="UNCONFIRMED",
            reason="Timestamp is in the future; unconfirmed by server",
        )

    # Calculate age in seconds
    age_delta = norm_current - norm_last_updated
    age_seconds = max(0.0, age_delta.total_seconds())

    if age_delta <= threshold:
        hours_ago = round(age_seconds / 3600.0, 1)
        return FreshnessResult(
            freshness_status=FreshnessStatus.FRESH,
            age_seconds=age_seconds,
            is_current=True,
            display_status="CONFIRMED",
            reason=f"Updated {hours_ago} hours ago (within {threshold.total_seconds() / 3600.0:.0f}h threshold)",
        )
    else:
        hours_ago = round(age_seconds / 3600.0, 1)
        return FreshnessResult(
            freshness_status=FreshnessStatus.STALE,
            age_seconds=age_seconds,
            is_current=False,
            display_status="OUTDATED",
            reason=f"Last updated {hours_ago} hours ago (exceeds {threshold.total_seconds() / 3600.0:.0f}h threshold)",
        )


def get_display_availability(
    quantity: Optional[int],
    last_updated: Optional[datetime],
    current_time: Optional[datetime] = None,
    availability_config: Optional[AvailabilityConfig] = None,
    freshness_threshold: timedelta = DEFAULT_FRESHNESS_THRESHOLD,
) -> DisplayAvailabilityResult:
    """
    Synthesize quantity and freshness into a safe user-facing display status.

    Safety rules:
    - Missing quantity remains UNKNOWN regardless of timestamp.
    - Stale known quantity displays OUTDATED to prevent misleading patients.
    - Fresh known quantity displays its confirmed stock status (AVAILABLE, LOW_STOCK, OUT_OF_STOCK).
    - Future/invalid timestamps display UNKNOWN / OUTDATED.

    Args:
        quantity: Current stock quantity (None or non-negative integer).
        last_updated: Timestamp of stock report.
        current_time: Injected reference clock.
        availability_config: Thresholds for low stock classification.
        freshness_threshold: Maximum age before a report is considered stale.

    Returns:
        DisplayAvailabilityResult dataclass.
    """
    cfg = availability_config or DEFAULT_AVAILABILITY_CONFIG
    reported = classify_availability(quantity, cfg)
    freshness = evaluate_freshness(last_updated, current_time, freshness_threshold)

    # If quantity is unknown, display is always UNKNOWN
    if reported == AvailabilityStatus.UNKNOWN:
        return DisplayAvailabilityResult(
            reported_status=AvailabilityStatus.UNKNOWN,
            freshness_status=freshness.freshness_status,
            display_status=DisplayStatus.UNKNOWN,
            is_confirmed=False,
            age_seconds=freshness.age_seconds,
            reason="Quantity has not been reported by the pharmacy",
        )

    # If timestamp is invalid or in the future
    if freshness.freshness_status == FreshnessStatus.FUTURE_INVALID:
        return DisplayAvailabilityResult(
            reported_status=reported,
            freshness_status=freshness.freshness_status,
            display_status=DisplayStatus.OUTDATED,
            is_confirmed=False,
            age_seconds=None,
            reason=f"Reported {reported}, but timestamp is implausible ({freshness.reason})",
        )

    # If timestamp is missing
    if freshness.freshness_status == FreshnessStatus.MISSING:
        return DisplayAvailabilityResult(
            reported_status=reported,
            freshness_status=freshness.freshness_status,
            display_status=DisplayStatus.OUTDATED,
            is_confirmed=False,
            age_seconds=None,
            reason=f"Reported {reported}, but no verification timestamp is available",
        )

    # If timestamp is stale
    if freshness.freshness_status == FreshnessStatus.STALE:
        return DisplayAvailabilityResult(
            reported_status=reported,
            freshness_status=freshness.freshness_status,
            display_status=DisplayStatus.OUTDATED,
            is_confirmed=False,
            age_seconds=freshness.age_seconds,
            reason=f"Previously reported {reported}, but stock record is outdated ({freshness.reason})",
        )

    # Timestamp is fresh and quantity is known -> Confirmed display status
    return DisplayAvailabilityResult(
        reported_status=reported,
        freshness_status=FreshnessStatus.FRESH,
        display_status=reported,
        is_confirmed=True,
        age_seconds=freshness.age_seconds,
        reason=f"Confirmed {reported} ({freshness.reason})",
    )
