"""
geocode.py — Unified reverse geocoding router.

Query flow:
    1. Check places DB for a close personal marker (within PLACE_AT_RADIUS)
       → return "{place name}" directly
    2. Try each installed map plugin (check if coordinate is in range)
       → return "{city}{district}{street}{housenumber}"
    3. Check places DB for a nearby personal marker (within PLACE_NEAR_RADIUS)
       as a last-resort hint if no map result
    4. Fallback: raw coordinates
"""

from __future__ import annotations

import importlib

from gps_geocoder.registry import list_maps, get_map_query

# If a saved place is within this radius, treat the user as "at" that place
# and return its name directly (highest priority over map-based geocoding).
PLACE_AT_RADIUS = 50

# If no map result is available, a place within this radius is used as a hint.
PLACE_NEAR_RADIUS = 500


def _in_bounds(lat: float, lng: float, bounds: tuple[float, float, float, float]) -> bool:
    lat_min, lat_max, lng_min, lng_max = bounds
    return lat_min <= lat <= lat_max and lng_min <= lng <= lng_max


def _place_result(place: dict, source: str) -> dict:
    return {
        "summary": place["name"],
        "place_name": place["name"],
        "address": place.get("address"),
        "source": source,
        "city": None,
        "district": None,
        "village": None,
        "street": None,
        "poi": place["name"],
        "poi_distance_m": place.get("distance_m"),
    }


def reverse_geocode(lat: float, lng: float) -> dict:
    """
    Reverse geocode a coordinate using all available sources.

    Returns dict with at least: summary, source, lat, lng
    """
    # 1. Close personal marker takes priority over map-based geocoding.
    try:
        from gps_geocoder.places import find_nearest_place
        at_place = find_nearest_place(lat, lng, radius_m=PLACE_AT_RADIUS)
        if at_place:
            return _place_result(at_place, source="places:at")
    except (ImportError, FileNotFoundError):
        pass

    # 2. Try installed map plugins
    available_maps = list_maps()
    for m in available_maps:
        map_id = m["id"]
        if not m["built"]:
            continue
        try:
            mod = importlib.import_module(f"gps_geocoder.maps.{map_id}")
            bounds = getattr(mod, "MAP_BOUNDS", None)
        except ImportError:
            bounds = None
        if bounds and not _in_bounds(lat, lng, bounds):
            continue
        try:
            query_mod = get_map_query(map_id)
            result = query_mod.reverse_geocode(lat, lng)
            if result and result.get("summary"):
                result["source"] = f"map:{map_id}"
                return result
        except (FileNotFoundError, ImportError):
            continue

    # 3. No map result — fall back to a nearby place marker as a hint.
    try:
        from gps_geocoder.places import find_nearest_place
        near_place = find_nearest_place(lat, lng, radius_m=PLACE_NEAR_RADIUS)
        if near_place:
            return _place_result(near_place, source="places:near")
    except (ImportError, FileNotFoundError):
        pass

    # 4. Fallback: raw coordinates
    return {
        "summary": f"{lat:.5f}, {lng:.5f}",
        "source": "none",
        "city": None,
        "district": None,
        "village": None,
        "street": None,
        "poi": None,
    }
