"""
MediBot tool adapters and catalogue providers for Django backend integration.

Decoupled bridge between Django ORM models and MediBot independent tool protocols.
MediBot remains independent of Django by accepting injected providers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from django.db import models
from apps.medicines.models import Medicine
from apps.pharmacies.models import Pharmacy, VerificationStatus
from core_intelligence.location.distance import calculate_distance_safe
import html
from apps.inventory.models import Inventory
from medibot.tools.medicine_search import MedicineSearchTool
from medibot.tools.pharmacy_search import PharmacySearchTool

GENERIC_PHARMACY_QUERIES = {
    "pharmacy", "pharmacies", "chemist", "chemists", "nearby", "medical store",
    "medical stores", "find nearby pharmacies", "find nearby pharmacy",
    "find pharmacies", "find pharmacy", "nearby pharmacies", "nearby pharmacy",
    "pharmacies near me", "pharmacy near me", "chemists near me", "medical stores near me"
}


class DjangoMedicineCatalogueProvider:
    """
    Catalogue provider reading medicine formulary records from the Django database.
    Feeds standard dictionaries into MediBot's MedicineSearchTool without coupling
    MediBot to Django models or PostgreSQL.
    """

    def __call__(self) -> List[Dict[str, Any]]:
        """
        Query Django Medicine records and return standardized dictionaries.
        Safely unescapes any HTML/hex entities at the data boundary.
        """
        queryset = Medicine.objects.values(
            "id",
            "generic_name",
            "brand_name",
            "strength",
            "dosage_form",
            "pack_size",
            "search_aliases",
        )
        results = []
        for row in queryset:
            results.append({
                "id": row["id"],
                "generic_name": html.unescape(row["generic_name"]) if row["generic_name"] else "",
                "brand_name": html.unescape(row["brand_name"]) if row["brand_name"] else "",
                "strength": html.unescape(row["strength"]) if row["strength"] else "",
                "dosage_form": html.unescape(row["dosage_form"]) if row["dosage_form"] else "",
                "pack_size": row["pack_size"],
                "search_aliases": [
                    html.unescape(a) for a in (row["search_aliases"] or []) if a
                ],
            })
        return results


class DjangoPharmacyProvider:
    """
    Pharmacy provider reading verified pharmacy establishments and real inventory records
    from the Django database. Feeds standard dictionaries into MediBot's PharmacySearchTool
    without coupling MediBot to Django models or PostgreSQL.
    """

    def __call__(
        self,
        query: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        max_radius_km: Optional[float] = None,
        limit: Optional[int] = 5,
        medicine_name: Optional[str] = None,
        medicine_id: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        # Case A: Medicine context provided — search inventory records of verified pharmacies
        med_objs: List[Medicine] = []
        if medicine_id:
            try:
                med_objs = list(Medicine.objects.filter(id=medicine_id))
            except (ValueError, TypeError):
                med_objs = []

        if not med_objs and medicine_name:
            # 1. Try Core Intelligence fuzzy matching first
            try:
                from core_intelligence.search_engine.matching import search_medicines
                all_meds = list(Medicine.objects.values(
                    "id", "generic_name", "brand_name", "strength", "dosage_form", "pack_size", "search_aliases"
                ))
                matches = search_medicines(medicine_name, all_meds, fuzzy_threshold=0.60)
                if matches:
                    matched_ids = [m["medicine"]["id"] for m in matches[:3]]
                    med_objs = list(Medicine.objects.filter(id__in=matched_ids))
            except Exception:
                pass

            # 2. Fallback to SQL icontains match
            if not med_objs:
                clean_med = html.unescape(medicine_name).strip()
                med_objs = list(Medicine.objects.filter(
                    models.Q(brand_name__icontains=clean_med)
                    | models.Q(generic_name__icontains=clean_med)
                ))
                if not med_objs and clean_med:
                    first_token = clean_med.split()[0]
                    if len(first_token) >= 3:
                        med_objs = list(Medicine.objects.filter(
                            models.Q(brand_name__icontains=first_token)
                            | models.Q(generic_name__icontains=first_token)
                        ))

        if med_objs:
            inv_qs = Inventory.objects.filter(
                medicine__in=med_objs,
                pharmacy__verification_status=VerificationStatus.VERIFIED,
            ).select_related("pharmacy", "medicine")

            if query:
                clean_q = query.strip()
                if (
                    clean_q.lower() not in GENERIC_PHARMACY_QUERIES
                    and (not medicine_name or clean_q.lower() not in medicine_name.lower())
                ):
                    inv_qs = inv_qs.filter(
                        models.Q(pharmacy__name__icontains=clean_q)
                        | models.Q(pharmacy__area__icontains=clean_q)
                        | models.Q(pharmacy__city__icontains=clean_q)
                    )

            results: List[Dict[str, Any]] = []
            for inv in inv_qs:
                p = inv.pharmacy
                m = inv.medicine

                dist_km = None
                if lat is not None and lon is not None and p.latitude is not None and p.longitude is not None:
                    dist_km = calculate_distance_safe(lat, lon, float(p.latitude), float(p.longitude))
                    if max_radius_km and dist_km and dist_km > max_radius_km:
                        continue

                status_key, status_label = inv.get_availability_status()
                price_val = float(inv.price) if inv.price is not None else None

                pharm_dict = {
                    "id": p.id,
                    "name": html.unescape(p.name),
                    "address": html.unescape(p.address),
                    "area": html.unescape(p.area),
                    "city": html.unescape(p.city),
                    "pin_code": p.pin_code,
                    "contact_number": p.contact_number,
                    "distance_km": dist_km,
                    "is_demo": p.is_demo,
                }

                med_dict = {
                    "id": m.id,
                    "generic_name": html.unescape(m.generic_name),
                    "brand_name": html.unescape(m.brand_name) if m.brand_name else "",
                    "strength": html.unescape(m.strength) if m.strength else "",
                    "dosage_form": m.dosage_form,
                }

                results.append({
                    "id": inv.id,
                    "pharmacy": pharm_dict,
                    "medicine": med_dict,
                    "quantity": inv.quantity,
                    "stock_status": status_key,
                    "stock_status_label": status_label,
                    "price": price_val,
                    "distance_km": dist_km,
                    "is_demo": inv.is_demo or p.is_demo,
                    "last_updated": inv.last_updated.isoformat() if inv.last_updated else None,
                    # Flat fields for general backwards compatibility:
                    "name": pharm_dict["name"],
                    "address": pharm_dict["address"],
                    "area": pharm_dict["area"],
                    "city": pharm_dict["city"],
                    "pin_code": pharm_dict["pin_code"],
                    "contact_number": pharm_dict["contact_number"],
                })

            if lat is not None and lon is not None:
                results.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"]))

            return results[: (limit or 5)]

        # If a specific medicine was searched for but not found in catalogue, return empty truthfully
        if medicine_name or medicine_id:
            return []

        # Case B: General pharmacy directory search (no medicine specified)
        qs = Pharmacy.objects.filter(verification_status=VerificationStatus.VERIFIED)
        if query:
            clean_q = query.strip()
            if clean_q.lower() not in GENERIC_PHARMACY_QUERIES:
                qs = qs.filter(
                    models.Q(name__icontains=clean_q)
                    | models.Q(area__icontains=clean_q)
                    | models.Q(city__icontains=clean_q)
                )

        results = []
        for p in qs:
            dist_km = None
            if lat is not None and lon is not None and p.latitude is not None and p.longitude is not None:
                dist_km = calculate_distance_safe(lat, lon, float(p.latitude), float(p.longitude))
                if max_radius_km and dist_km and dist_km > max_radius_km:
                    continue

            pharm_dict = {
                "id": p.id,
                "name": html.unescape(p.name),
                "address": html.unescape(p.address),
                "area": html.unescape(p.area),
                "city": html.unescape(p.city),
                "pin_code": p.pin_code,
                "contact_number": p.contact_number,
                "distance_km": dist_km,
                "is_demo": p.is_demo,
            }
            results.append({
                **pharm_dict,
                "pharmacy": pharm_dict,
            })

        if lat is not None and lon is not None:
            results.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"]))

        return results[: (limit or 5)]


def get_django_medicine_search_tool() -> MedicineSearchTool:
    """
    Factory creating a MedicineSearchTool wired to DjangoMedicineCatalogueProvider.
    """
    provider = DjangoMedicineCatalogueProvider()
    return MedicineSearchTool(catalogue_provider=provider)


def get_django_pharmacy_search_tool() -> PharmacySearchTool:
    """
    Factory creating a PharmacySearchTool connected to DjangoPharmacyProvider.
    """
    provider = DjangoPharmacyProvider()
    return PharmacySearchTool(pharmacy_provider=provider)
