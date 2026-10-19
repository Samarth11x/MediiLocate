"""
Search API views for MediLocate AI.

Exposes read-only endpoints:
- GET /api/v1/search/medicines/
  Accepts query string and optional user coordinates (lat, lon, radius).
  Matches medicines using Core Intelligence matching algorithms, then queries
  verified pharmacy inventories and ranks stores using Core Intelligence composite heuristics.
- GET /api/v1/search/pharmacies/
  Accepts optional medicine_id or query string and optional coordinates.
  Returns verified pharmacies with inventory and distance ranking.

Preserves:
- Strict medicine identity safeguards (strength/form mismatches are excluded).
- 4 inventory states: AVAILABLE, LOW_STOCK, OUT_OF_STOCK, and UNKNOWN.
- Unverified pharmacies strictly excluded.
- Conspicuous demonstration disclosure.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import models

from apps.medicines.models import Medicine
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.inventory.models import Inventory

from core_intelligence.search_engine.matching import search_medicines
from core_intelligence.ranking.scoring import rank_candidates
from core_intelligence.location.distance import calculate_distance_safe


DEMO_DISCLOSURE_NOTICE = (
    "DEMO MODE — All pharmacy listings, locations, prices, and inventory shown here "
    "are fictional examples and are not real-time pharmacy information."
)


def _validate_coordinates(lat_raw: Any, lon_raw: Any) -> Optional[tuple[float, float]]:
    """
    Validate lat/lon query params.
    Returns (lat, lon) as floats if both valid, None if both omitted.
    Raises ValueError on invalid formats or bounds.
    """
    if lat_raw is None and lon_raw is None:
        return None

    if lat_raw is None or lon_raw is None:
        raise ValueError("Both 'lat' and 'lon' parameters must be provided together.")

    try:
        lat = float(lat_raw)
        lon = float(lon_raw)
    except (TypeError, ValueError):
        raise ValueError("'lat' and 'lon' must be valid numeric floating-point values.")

    if not (-90.0 <= lat <= 90.0):
        raise ValueError("Latitude must be between -90.0 and 90.0 degrees.")

    if not (-180.0 <= lon <= 180.0):
        raise ValueError("Longitude must be between -180.0 and 180.0 degrees.")

    return (lat, lon)


class MedicineSearchView(APIView):
    """
    Medicine catalog search and pharmacy availability endpoint.
    GET /api/v1/search/medicines/?query=...[&lat=...&lon=...&radius=...&limit=...]
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # 1. Validate query string
        raw_query = request.query_params.get("query")
        if raw_query is None:
            return Response(
                {"error": "The 'query' parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = str(raw_query).strip()
        if not query:
            return Response(
                {"error": "The 'query' parameter cannot be empty or whitespace only."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(query) > 200:
            return Response(
                {"error": "The 'query' parameter cannot exceed 200 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Validate coordinates
        lat_raw = request.query_params.get("lat")
        lon_raw = request.query_params.get("lon")
        try:
            coords = _validate_coordinates(lat_raw, lon_raw)
        except ValueError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        user_lat, user_lon = coords if coords else (None, None)

        # 3. Validate radius and limit
        try:
            radius_km = float(request.query_params.get("radius", 50.0))
            if radius_km <= 0 or radius_km > 500.0:
                return Response(
                    {"error": "'radius' must be a positive number up to 500.0 km."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response(
                {"error": "'radius' must be a valid numeric value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            limit = int(request.query_params.get("limit", 10))
            if limit < 1 or limit > 50:
                return Response(
                    {"error": "'limit' must be an integer between 1 and 50."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response(
                {"error": "'limit' must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4. Fetch all active medicines for Core Intelligence matching
        all_medicines = list(
            Medicine.objects.values(
                "id",
                "generic_name",
                "brand_name",
                "strength",
                "dosage_form",
                "pack_size",
                "search_aliases",
            )
        )

        if not all_medicines:
            return Response(
                {
                    "query": query,
                    "total_medicines": 0,
                    "medicines": [],
                    "total_pharmacies": 0,
                    "pharmacies": [],
                    "user_location": None,
                    "message": "Medicine catalogue is currently unpopulated in this development environment.",
                    "demo_notice": DEMO_DISCLOSURE_NOTICE,
                },
                status=status.HTTP_200_OK,
            )

        # 5. Core Intelligence search matching
        matches = search_medicines(query=query, medicines=all_medicines, limit=limit)

        if not matches:
            return Response(
                {
                    "query": query,
                    "total_medicines": 0,
                    "medicines": [],
                    "total_pharmacies": 0,
                    "pharmacies": [],
                    "user_location": {"lat": user_lat, "lon": user_lon} if user_lat is not None else None,
                    "message": f"No medicines found matching '{query}'.",
                    "demo_notice": DEMO_DISCLOSURE_NOTICE,
                },
                status=status.HTTP_200_OK,
            )

        # 6. Format matched medicines
        serialized_meds = []
        for d in matches:
            serialized_meds.append({
                "id": d["medicine"]["id"],
                "generic_name": d["medicine"]["generic_name"],
                "brand_name": d["medicine"]["brand_name"],
                "strength": d["medicine"]["strength"],
                "dosage_form": d["medicine"]["dosage_form"],
                "pack_size": d["medicine"].get("pack_size"),
                "match_score": d["match_score"],
                "match_type": d["match_type"],
                "matched_fields": d["matched_fields"],
                "explanation": d["explanation"],
            })

        # 7. Find inventory links at VERIFIED pharmacies for matched medicines
        matched_med_ids = [m["id"] for m in serialized_meds]
        med_score_map = {m["id"]: m["match_score"] for m in serialized_meds}

        inventory_qs = Inventory.objects.filter(
            medicine_id__in=matched_med_ids,
            pharmacy__verification_status=VerificationStatus.VERIFIED,
        ).select_related("pharmacy", "medicine")

        # 8. Build candidate list for Core Intelligence ranking engine
        candidates: List[Dict[str, Any]] = []

        for inv in inventory_qs:
            pharm = inv.pharmacy
            med = inv.medicine

            dist_km = None
            if user_lat is not None and user_lon is not None and pharm.latitude and pharm.longitude:
                dist_km = calculate_distance_safe(
                    user_lat,
                    user_lon,
                    float(pharm.latitude),
                    float(pharm.longitude),
                )
                if dist_km is not None and dist_km > radius_km:
                    continue  # Filter out stores exceeding requested radius

            rel_score = med_score_map.get(med.id, 0.5)

            candidates.append({
                "inventory_id": inv.id,
                "pharmacy": {
                    "id": pharm.id,
                    "name": pharm.name,
                    "address": pharm.address,
                    "area": pharm.area,
                    "city": pharm.city,
                    "pin_code": pharm.pin_code,
                    "latitude": float(pharm.latitude) if pharm.latitude else None,
                    "longitude": float(pharm.longitude) if pharm.longitude else None,
                    "contact_number": pharm.contact_number,
                    "verification_status": pharm.verification_status,
                    "opening_hours": pharm.opening_hours,
                    "is_demo": pharm.is_demo,
                },
                "medicine": {
                    "id": med.id,
                    "name": str(med),
                    "generic_name": med.generic_name,
                    "brand_name": med.brand_name,
                    "strength": med.strength,
                    "dosage_form": med.dosage_form,
                    "pack_size": med.pack_size,
                },
                "match_score": rel_score,
                "quantity": inv.quantity,
                "unit_price": float(inv.price) if inv.price is not None else None,
                "last_updated": inv.last_updated,
                "distance_km": dist_km,
                "is_demo": inv.is_demo,
            })

        # 9. Execute Core Intelligence composite ranking
        ranked_candidates = rank_candidates(candidates)

        # 10. Format final pharmacy results
        pharmacy_results = []
        for r in ranked_candidates:
            raw_status = r["display_status"]
            pharmacy_results.append({
                "inventory_id": r["inventory_id"],
                "pharmacy": r["pharmacy"],
                "medicine": r["medicine"],
                "stock_status": raw_status,
                "stock_label": raw_status.replace("_", " ").title(),
                "quantity": r["quantity"],
                "price": f"{r['unit_price']:.2f}" if r.get("unit_price") is not None else None,
                "distance_km": r.get("distance_km"),
                "ranking_score": r.get("ranking_score", 0.0),
                "ranking_reasons": r.get("reason_codes", []),
                "ranking_explanation": r.get("explanation", ""),
                "is_demo": r.get("is_demo", True),
            })

        return Response(
            {
                "query": query,
                "total_medicines": len(serialized_meds),
                "medicines": serialized_meds,
                "total_pharmacies": len(pharmacy_results),
                "pharmacies": pharmacy_results,
                "user_location": {"lat": user_lat, "lon": user_lon} if user_lat is not None else None,
                "demo_notice": DEMO_DISCLOSURE_NOTICE,
            },
            status=status.HTTP_200_OK,
        )


class PharmacySearchView(APIView):
    """
    Pharmacy search and listing endpoint.
    GET /api/v1/search/pharmacies/?medicine_id=...[&lat=...&lon=...&radius=...&query=...]
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # 1. Coordinates validation
        lat_raw = request.query_params.get("lat")
        lon_raw = request.query_params.get("lon")
        try:
            coords = _validate_coordinates(lat_raw, lon_raw)
        except ValueError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        user_lat, user_lon = coords if coords else (None, None)

        # 2. Medicine ID validation
        medicine_id = request.query_params.get("medicine_id")
        med_obj = None
        if medicine_id is not None:
            try:
                med_obj = Medicine.objects.get(id=int(medicine_id))
            except (ValueError, Medicine.DoesNotExist):
                return Response(
                    {"error": f"Medicine with id '{medicine_id}' does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # 3. Base queryset: Strictly verified pharmacies only
        pharmacies_qs = Pharmacy.objects.filter(verification_status=VerificationStatus.VERIFIED)

        pharm_query = request.query_params.get("query")
        if pharm_query and str(pharm_query).strip():
            pq = str(pharm_query).strip()
            pharmacies_qs = pharmacies_qs.filter(
                models.Q(name__icontains=pq)
                | models.Q(area__icontains=pq)
                | models.Q(city__icontains=pq)
            )

        # If a specific medicine was requested, attach inventory data
        candidates = []
        for pharm in pharmacies_qs:
            dist_km = None
            if user_lat is not None and user_lon is not None and pharm.latitude and pharm.longitude:
                dist_km = calculate_distance_safe(
                    user_lat,
                    user_lon,
                    float(pharm.latitude),
                    float(pharm.longitude),
                )

            inv_obj = None
            if med_obj:
                inv_obj = Inventory.objects.filter(pharmacy=pharm, medicine=med_obj).first()

            candidates.append({
                "pharmacy": {
                    "id": pharm.id,
                    "name": pharm.name,
                    "address": pharm.address,
                    "area": pharm.area,
                    "city": pharm.city,
                    "pin_code": pharm.pin_code,
                    "latitude": float(pharm.latitude) if pharm.latitude else None,
                    "longitude": float(pharm.longitude) if pharm.longitude else None,
                    "contact_number": pharm.contact_number,
                    "verification_status": pharm.verification_status,
                    "opening_hours": pharm.opening_hours,
                    "is_demo": pharm.is_demo,
                },
                "medicine": {
                    "id": med_obj.id,
                    "name": str(med_obj),
                    "generic_name": med_obj.generic_name,
                    "brand_name": med_obj.brand_name,
                    "strength": med_obj.strength,
                    "dosage_form": med_obj.dosage_form,
                } if med_obj else None,
                "match_score": 1.0,
                "quantity": inv_obj.quantity if inv_obj else None,
                "unit_price": float(inv_obj.price) if (inv_obj and inv_obj.price is not None) else None,
                "last_updated": inv_obj.last_updated if inv_obj else None,
                "distance_km": dist_km,
                "is_demo": pharm.is_demo,
            })

        ranked_candidates = rank_candidates(candidates)

        results = []
        for r in ranked_candidates:
            results.append({
                "pharmacy": r["pharmacy"],
                "medicine": r.get("medicine"),
                "stock_status": r["display_status"] if med_obj else None,
                "stock_label": r["display_status"].replace("_", " ").title() if med_obj else None,
                "quantity": r.get("quantity"),
                "price": f"{r['unit_price']:.2f}" if r.get("unit_price") is not None else None,
                "distance_km": r.get("distance_km"),
                "ranking_score": r.get("ranking_score", 0.0),
                "ranking_explanation": r.get("explanation", ""),
                "is_demo": r.get("is_demo", True),
            })

        return Response(
            {
                "total_pharmacies": len(results),
                "pharmacies": results,
                "user_location": {"lat": user_lat, "lon": user_lon} if user_lat is not None else None,
                "demo_notice": DEMO_DISCLOSURE_NOTICE,
            },
            status=status.HTTP_200_OK,
        )
