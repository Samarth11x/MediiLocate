"""
Unit tests for Haversine geographic distance calculation and radius filtering.
"""

import math
import pytest
from core_intelligence.location.distance import (
    haversine_km,
    calculate_distance_safe,
    filter_by_radius,
    EARTH_RADIUS_KM,
)


class TestHaversineDistance:
    """Tests for great-circle distance accuracy, boundary conditions, and error handling."""

    def test_same_coordinates(self):
        assert haversine_km(12.9716, 77.5946, 12.9716, 77.5946) == 0.0
        assert haversine_km(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_known_equatorial_degree_distance(self):
        # 1 degree of longitude at the equator should be ~111.195 km
        expected = (2.0 * math.pi * EARTH_RADIUS_KM) / 360.0
        dist = haversine_km(0.0, 0.0, 0.0, 1.0)
        assert abs(dist - expected) < 0.01

    def test_known_city_pair_distance(self):
        # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ~ 343.5 km
        dist = haversine_km(51.5074, -0.1278, 48.8566, 2.3522)
        assert 340.0 < dist < 348.0

    def test_distance_symmetry(self):
        # Distance A -> B must equal distance B -> A
        pt1 = (19.0760, 72.8777)  # Mumbai
        pt2 = (28.6139, 77.2090)  # Delhi
        dist_forward = haversine_km(pt1[0], pt1[1], pt2[0], pt2[1])
        dist_reverse = haversine_km(pt2[0], pt2[1], pt1[0], pt1[1])
        assert dist_forward == dist_reverse
        assert 1100.0 < dist_forward < 1200.0

    def test_antimeridian_crossing(self):
        # Coordinates across the 180th meridian: 179°E to -179°W at the equator (2 degrees apart)
        dist = haversine_km(0.0, 179.0, 0.0, -179.0)
        expected_2_deg = (2.0 * math.pi * EARTH_RADIUS_KM) / 180.0
        assert abs(dist - expected_2_deg) < 0.1

    def test_invalid_latitude_raises_value_error(self):
        with pytest.raises(ValueError, match="Origin latitude"):
            haversine_km(95.0, 0.0, 10.0, 10.0)
        with pytest.raises(ValueError, match="Destination latitude"):
            haversine_km(0.0, 0.0, -90.5, 0.0)

    def test_invalid_longitude_raises_value_error(self):
        with pytest.raises(ValueError, match="Origin longitude"):
            haversine_km(0.0, 185.0, 10.0, 10.0)
        with pytest.raises(ValueError, match="Destination longitude"):
            haversine_km(0.0, 0.0, 10.0, -181.0)

    def test_non_finite_inputs_raise_value_error(self):
        with pytest.raises(ValueError):
            haversine_km(float("nan"), 0.0, 10.0, 10.0)
        with pytest.raises(ValueError):
            haversine_km(0.0, 0.0, float("inf"), 10.0)

    def test_non_numeric_inputs_raise_type_error(self):
        with pytest.raises(TypeError):
            haversine_km(None, 0.0, 10.0, 10.0)  # type: ignore
        with pytest.raises(TypeError):
            haversine_km(True, 0.0, 10.0, 10.0)  # type: ignore
        with pytest.raises(TypeError):
            haversine_km("12.5", 0.0, 10.0, 10.0)  # type: ignore


class TestDistanceSafeAndRadiusFilter:
    """Tests for safe wrappers and radius filtering."""

    def test_calculate_distance_safe(self):
        # Valid coordinates
        assert calculate_distance_safe(0.0, 0.0, 0.0, 1.0) is not None
        # Invalid / missing coordinates should return None without crashing
        assert calculate_distance_safe(None, 0.0, 10.0, 10.0) is None
        assert calculate_distance_safe(95.0, 0.0, 10.0, 10.0) is None
        assert calculate_distance_safe("invalid", 0.0, 10.0, 10.0) is None

    def test_filter_by_radius(self):
        user_loc = (12.9716, 77.5946)
        pharmacies = [
            {"id": "p1", "latitude": 12.9750, "longitude": 77.5980},  # ~0.5 km
            {"id": "p2", "latitude": 12.9900, "longitude": 77.6100},  # ~2.6 km
            {"id": "p3", "latitude": 13.5000, "longitude": 78.0000},  # ~70 km
            {"id": "p4", "latitude": None, "longitude": 77.5980},     # invalid
        ]

        # 5 km radius should include p1 and p2, exclude p3 and p4
        nearby = filter_by_radius(user_loc[0], user_loc[1], pharmacies, max_radius_km=5.0)
        assert len(nearby) == 2
        assert nearby[0]["id"] == "p1"
        assert nearby[1]["id"] == "p2"
        # distance_km should be attached and sorted
        assert nearby[0]["distance_km"] < nearby[1]["distance_km"]
