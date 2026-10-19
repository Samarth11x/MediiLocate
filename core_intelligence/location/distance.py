"""
Geographic distance calculation module.

Provides a pure Python, validated Haversine formula implementation for
great-circle distance calculation between two geographic coordinates on Earth.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

# Mean Earth radius in kilometres (IUGG / WGS84 standard spherical mean)
EARTH_RADIUS_KM: float = 6371.0


def _validate_coordinate(val: Any, name: str, min_val: float, max_val: float) -> float:
    """
    Validate that a coordinate value is numeric, finite, and within valid bounds.

    Args:
        val: Input coordinate value.
        name: Name of coordinate (e.g. 'Latitude', 'Longitude').
        min_val: Minimum permitted value.
        max_val: Maximum permitted value.

    Returns:
        Validated float.

    Raises:
        TypeError: If val is not a numeric type.
        ValueError: If val is non-finite or out of bounds.
    """
    if val is None or isinstance(val, bool) or not isinstance(val, (int, float)):
        raise TypeError(f"{name} must be numeric (int or float), got {type(val).__name__} ({val})")

    f_val = float(val)

    if not math.isfinite(f_val):
        raise ValueError(f"{name} must be a finite number, got {f_val}")

    if not (min_val <= f_val <= max_val):
        raise ValueError(
            f"{name} must be between {min_val} and {max_val} degrees, got {f_val}"
        )

    return f_val


def haversine_km(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula.

    Coordinate ordering: (latitude, longitude) in decimal degrees.
    - Latitude must be in [-90.0, 90.0].
    - Longitude must be in [-180.0, 180.0].

    Distance is a straight-line great-circle estimate, not guaranteed road travel.

    Args:
        origin_lat: Starting latitude in degrees.
        origin_lon: Starting longitude in degrees.
        destination_lat: Target latitude in degrees.
        destination_lon: Target longitude in degrees.

    Returns:
        Great-circle distance in kilometres (float >= 0.0).

    Raises:
        TypeError: If coordinates are non-numeric.
        ValueError: If coordinates are out of valid geographic range or non-finite.
    """
    lat1 = _validate_coordinate(origin_lat, "Origin latitude", -90.0, 90.0)
    lon1 = _validate_coordinate(origin_lon, "Origin longitude", -180.0, 180.0)
    lat2 = _validate_coordinate(destination_lat, "Destination latitude", -90.0, 90.0)
    lon2 = _validate_coordinate(destination_lon, "Destination longitude", -180.0, 180.0)

    # Identical coordinates
    if lat1 == lat2 and lon1 == lon2:
        return 0.0

    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )

    # Clamp 'a' to [0.0, 1.0] to safeguard against precision errors
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = EARTH_RADIUS_KM * c
    return round(distance, 4)


def calculate_distance_safe(
    origin_lat: Any,
    origin_lon: Any,
    dest_lat: Any,
    dest_lon: Any,
) -> Optional[float]:
    """
    Safely calculate distance without raising exceptions on missing or malformed inputs.

    Never fabricates distances for missing or invalid locations.

    Args:
        origin_lat: Starting latitude.
        origin_lon: Starting longitude.
        dest_lat: Target latitude.
        dest_lon: Target longitude.

    Returns:
        Calculated distance in km, or None if coordinates are missing or invalid.
    """
    try:
        return haversine_km(origin_lat, origin_lon, dest_lat, dest_lon)
    except (TypeError, ValueError):
        return None


def filter_by_radius(
    origin_lat: float,
    origin_lon: float,
    items: List[Dict[str, Any]],
    max_radius_km: float,
    lat_key: str = "latitude",
    lon_key: str = "longitude",
) -> List[Dict[str, Any]]:
    """
    Filter a list of items having latitude/longitude within a given radius in km.
    Appends 'distance_km' to each returned item copy, sorted from nearest to farthest.

    Args:
        origin_lat: Reference user latitude.
        origin_lon: Reference user longitude.
        items: List of dictionaries containing geographic coordinates.
        max_radius_km: Maximum radius in kilometres.
        lat_key: Key in dictionary storing latitude.
        lon_key: Key in dictionary storing longitude.

    Returns:
        List of matching item dictionaries within the radius, with 'distance_km' attached,
        sorted by distance ascending.
    """
    if max_radius_km <= 0 or not items:
        return []

    within_radius = []
    for item in items:
        if not isinstance(item, dict):
            continue

        item_lat = item.get(lat_key)
        item_lon = item.get(lon_key)
        dist = calculate_distance_safe(origin_lat, origin_lon, item_lat, item_lon)

        if dist is not None and dist <= max_radius_km:
            item_copy = dict(item)
            item_copy["distance_km"] = dist
            within_radius.append(item_copy)

    within_radius.sort(key=lambda x: x["distance_km"])
    return within_radius
