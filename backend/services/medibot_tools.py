"""
MediBot tool adapters and catalogue providers for Django backend integration.

Decoupled bridge between Django ORM models and MediBot independent tool protocols.
MediBot remains independent of Django by accepting injected providers.
"""

from __future__ import annotations

from typing import Any, Dict, List
from apps.medicines.models import Medicine
from medibot.tools.medicine_search import MedicineSearchTool
from medibot.tools.pharmacy_search import PharmacySearchTool


class DjangoMedicineCatalogueProvider:
    """
    Catalogue provider reading medicine formulary records from the Django database.
    Feeds standard dictionaries into MediBot's MedicineSearchTool without coupling
    MediBot to Django models or PostgreSQL.
    """

    def __call__(self) -> List[Dict[str, Any]]:
        """
        Query Django Medicine records and return standardized dictionaries.
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
        return list(queryset)


def get_django_medicine_search_tool() -> MedicineSearchTool:
    """
    Factory creating a MedicineSearchTool wired to DjangoMedicineCatalogueProvider.
    """
    provider = DjangoMedicineCatalogueProvider()
    return MedicineSearchTool(catalogue_provider=provider)


def get_django_pharmacy_search_tool() -> PharmacySearchTool:
    """
    Factory creating a PharmacySearchTool.
    Returns honest 'unavailable' status until Phase 6 pharmacy location integration.
    """
    return PharmacySearchTool()
