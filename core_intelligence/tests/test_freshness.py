"""
Unit tests for inventory freshness and presentation status evaluation.
"""

import pytest
from datetime import datetime, timezone, timedelta
from core_intelligence.availability.freshness import (
    FreshnessStatus,
    DisplayStatus,
    evaluate_freshness,
    get_display_availability,
)
from core_intelligence.availability.rules import AvailabilityStatus


class TestFreshnessEvaluation:
    """Tests for assessing record age and freshness status."""

    def test_fresh_record(self, fixed_now: datetime):
        two_hours_ago = fixed_now - timedelta(hours=2)
        res = evaluate_freshness(two_hours_ago, current_time=fixed_now)
        assert res.freshness_status == FreshnessStatus.FRESH
        assert res.is_current is True
        assert res.display_status == "CONFIRMED"
        assert res.age_seconds == 7200.0

    def test_record_at_exact_threshold(self, fixed_now: datetime):
        threshold_24h = timedelta(hours=24)
        exactly_24h_ago = fixed_now - threshold_24h
        res = evaluate_freshness(exactly_24h_ago, current_time=fixed_now, threshold=threshold_24h)
        assert res.freshness_status == FreshnessStatus.FRESH
        assert res.is_current is True

    def test_stale_record(self, fixed_now: datetime):
        three_days_ago = fixed_now - timedelta(days=3)
        res = evaluate_freshness(three_days_ago, current_time=fixed_now)
        assert res.freshness_status == FreshnessStatus.STALE
        assert res.is_current is False
        assert res.display_status == "OUTDATED"
        assert res.age_seconds == 3 * 86400.0

    def test_missing_timestamp(self, fixed_now: datetime):
        res = evaluate_freshness(None, current_time=fixed_now)
        assert res.freshness_status == FreshnessStatus.MISSING
        assert res.is_current is False
        assert res.age_seconds is None
        assert res.display_status == "UNCONFIRMED"

    def test_future_timestamp_rejected(self, fixed_now: datetime):
        one_hour_future = fixed_now + timedelta(hours=1)
        res = evaluate_freshness(one_hour_future, current_time=fixed_now)
        assert res.freshness_status == FreshnessStatus.FUTURE_INVALID
        assert res.is_current is False
        assert "future" in res.reason.lower()

    def test_invalid_type_timestamp(self, fixed_now: datetime):
        res = evaluate_freshness("2026-10-19", current_time=fixed_now)  # type: ignore
        assert res.freshness_status == FreshnessStatus.FUTURE_INVALID
        assert res.is_current is False

    def test_timezone_naive_handling(self, fixed_now: datetime):
        # Naive datetime should be handled gracefully without crashing
        naive_dt = datetime(2026, 10, 19, 10, 0, 0)
        res = evaluate_freshness(naive_dt, current_time=fixed_now)
        assert res.freshness_status == FreshnessStatus.FRESH
        assert res.is_current is True


class TestCombinedDisplayAvailability:
    """Tests ensuring presentation rules prevent misleading users about stock."""

    def test_fresh_confirmed_available(self, fixed_now: datetime):
        two_hours_ago = fixed_now - timedelta(hours=2)
        res = get_display_availability(quantity=25, last_updated=two_hours_ago, current_time=fixed_now)
        assert res.reported_status == AvailabilityStatus.AVAILABLE
        assert res.display_status == DisplayStatus.AVAILABLE
        assert res.is_confirmed is True

    def test_fresh_confirmed_low_stock(self, fixed_now: datetime):
        one_hour_ago = fixed_now - timedelta(hours=1)
        res = get_display_availability(quantity=5, last_updated=one_hour_ago, current_time=fixed_now)
        assert res.reported_status == AvailabilityStatus.LOW_STOCK
        assert res.display_status == DisplayStatus.LOW_STOCK
        assert res.is_confirmed is True

    def test_fresh_confirmed_out_of_stock(self, fixed_now: datetime):
        half_hour_ago = fixed_now - timedelta(minutes=30)
        res = get_display_availability(quantity=0, last_updated=half_hour_ago, current_time=fixed_now)
        assert res.reported_status == AvailabilityStatus.OUT_OF_STOCK
        assert res.display_status == DisplayStatus.OUT_OF_STOCK
        assert res.is_confirmed is True

    def test_stale_stock_displays_outdated(self, fixed_now: datetime):
        """
        Critical Safeguard:
        A stale record with quantity=50 must display OUTDATED rather than
        misleading the user into thinking stock is currently AVAILABLE.
        """
        five_days_ago = fixed_now - timedelta(days=5)
        res = get_display_availability(quantity=50, last_updated=five_days_ago, current_time=fixed_now)
        assert res.reported_status == AvailabilityStatus.AVAILABLE
        assert res.display_status == DisplayStatus.OUTDATED
        assert res.is_confirmed is False
        assert "outdated" in res.reason.lower()

    def test_missing_quantity_always_unknown(self, fixed_now: datetime):
        """
        Even with a fresh timestamp, unknown quantity must remain UNKNOWN.
        """
        just_now = fixed_now - timedelta(minutes=5)
        res = get_display_availability(quantity=None, last_updated=just_now, current_time=fixed_now)
        assert res.reported_status == AvailabilityStatus.UNKNOWN
        assert res.display_status == DisplayStatus.UNKNOWN
        assert res.is_confirmed is False
