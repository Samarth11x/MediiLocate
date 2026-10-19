"""
Inventory availability classification rules.

Provides pure Python, configurable stock level classification compatible with
the MediLocate domain model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


class AvailabilityStatus:
    """Canonical inventory availability status constants."""
    AVAILABLE = "AVAILABLE"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    UNKNOWN = "UNKNOWN"

    ALL = {AVAILABLE, LOW_STOCK, OUT_OF_STOCK, UNKNOWN}


@dataclass(frozen=True)
class AvailabilityConfig:
    """
    Configuration for inventory availability evaluation.

    Attributes:
        low_stock_threshold: Units below which stock is classified as LOW_STOCK.
                              Default: 10 units (development setting).
    """
    low_stock_threshold: int = 10

    def __post_init__(self) -> None:
        if not isinstance(self.low_stock_threshold, int) or self.low_stock_threshold <= 0:
            raise ValueError("low_stock_threshold must be a positive integer")


# Default global instance for standard operations
DEFAULT_AVAILABILITY_CONFIG = AvailabilityConfig()


def validate_quantity(quantity: Any) -> Optional[int]:
    """
    Validate that an input quantity is either None (unknown) or a non-negative integer.

    Args:
        quantity: Candidate quantity value.

    Returns:
        Validated integer, or None if input was None.

    Raises:
        ValueError: If quantity is negative or an incompatible type.
    """
    if quantity is None:
        return None

    # Disallow bool (since bool is a subclass of int in Python: isinstance(True, int) is True)
    if isinstance(quantity, bool):
        raise ValueError(f"Invalid quantity type {type(quantity).__name__}; boolean is not allowed.")

    if not isinstance(quantity, int):
        try:
            # Check if it's an int-convertible float with no fractional part
            f = float(quantity)
            if not f.is_integer():
                raise ValueError(f"Quantity must be a whole integer, got {quantity}")
            quantity = int(f)
        except (TypeError, ValueError) as err:
            raise ValueError(f"Invalid quantity value: {quantity}") from err

    if quantity < 0:
        raise ValueError(f"Quantity cannot be negative, got {quantity}")

    return quantity


def classify_availability(
    quantity: Optional[int],
    config: Optional[AvailabilityConfig] = None,
) -> str:
    """
    Classify an inventory quantity into a canonical availability status.

    Rules:
    - quantity is None: UNKNOWN (stock not reported / confirmed)
    - quantity == 0: OUT_OF_STOCK (confirmed zero)
    - 0 < quantity < low_stock_threshold: LOW_STOCK
    - quantity >= low_stock_threshold: AVAILABLE

    Unknown quantity is NEVER silently converted to zero.

    Args:
        quantity: Stock count (None, 0, or positive integer).
        config: AvailabilityConfig instance. Defaults to DEFAULT_AVAILABILITY_CONFIG.

    Returns:
        One of 'AVAILABLE', 'LOW_STOCK', 'OUT_OF_STOCK', 'UNKNOWN'.

    Raises:
        ValueError: If quantity is negative or invalid.
    """
    cfg = config or DEFAULT_AVAILABILITY_CONFIG
    validated = validate_quantity(quantity)

    if validated is None:
        return AvailabilityStatus.UNKNOWN
    if validated == 0:
        return AvailabilityStatus.OUT_OF_STOCK
    if validated < cfg.low_stock_threshold:
        return AvailabilityStatus.LOW_STOCK
    return AvailabilityStatus.AVAILABLE
