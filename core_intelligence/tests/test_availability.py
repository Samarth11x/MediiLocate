"""
Unit tests for availability classification rules.
"""

import pytest
from core_intelligence.availability.rules import (
    AvailabilityStatus,
    AvailabilityConfig,
    classify_availability,
    validate_quantity,
)


class TestAvailabilityClassification:
    """Tests for quantity validation and stock classification."""

    def test_unknown_quantity(self):
        # Quantity not reported / unconfirmed
        assert classify_availability(None) == AvailabilityStatus.UNKNOWN

    def test_zero_quantity_out_of_stock(self):
        # Explicit zero stock
        assert classify_availability(0) == AvailabilityStatus.OUT_OF_STOCK

    def test_low_stock_boundary_conditions(self):
        cfg = AvailabilityConfig(low_stock_threshold=10)
        # 1 below threshold
        assert classify_availability(9, cfg) == AvailabilityStatus.LOW_STOCK
        assert classify_availability(1, cfg) == AvailabilityStatus.LOW_STOCK
        # Exactly at threshold
        assert classify_availability(10, cfg) == AvailabilityStatus.AVAILABLE

    def test_available_stock(self):
        cfg = AvailabilityConfig(low_stock_threshold=10)
        assert classify_availability(11, cfg) == AvailabilityStatus.AVAILABLE
        assert classify_availability(100, cfg) == AvailabilityStatus.AVAILABLE

    def test_negative_quantity_raises_value_error(self):
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            classify_availability(-1)
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            classify_availability(-50)

    def test_invalid_types_rejected(self):
        with pytest.raises(ValueError):
            classify_availability(True)  # Booleans disallowed
        with pytest.raises(ValueError):
            classify_availability("invalid")
        with pytest.raises(ValueError):
            classify_availability(3.14)  # Non-whole floats

    def test_custom_threshold(self):
        custom_cfg = AvailabilityConfig(low_stock_threshold=5)
        assert classify_availability(4, custom_cfg) == AvailabilityStatus.LOW_STOCK
        assert classify_availability(5, custom_cfg) == AvailabilityStatus.AVAILABLE

    def test_invalid_config_threshold(self):
        with pytest.raises(ValueError, match="positive integer"):
            AvailabilityConfig(low_stock_threshold=0)
        with pytest.raises(ValueError, match="positive integer"):
            AvailabilityConfig(low_stock_threshold=-5)

    def test_validate_quantity_helper(self):
        assert validate_quantity(None) is None
        assert validate_quantity(0) == 0
        assert validate_quantity(15) == 15
        assert validate_quantity("20") == 20
