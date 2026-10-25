"""
URL patterns for pharmacist portal endpoints in MediLocate AI.
"""

from django.urls import path
from .pharmacist_views import (
    PharmacistPharmacyView,
    PharmacistInventoryListView,
    PharmacistInventoryDetailView,
    PharmacistMedicineCatalogView,
    PharmacistBulkInventoryView,
)

urlpatterns = [
    path('pharmacy/', PharmacistPharmacyView.as_view(), name='pharmacist-pharmacy'),
    path('inventory/', PharmacistInventoryListView.as_view(), name='pharmacist-inventory-list'),
    path('inventory/bulk/', PharmacistBulkInventoryView.as_view(), name='pharmacist-inventory-bulk'),
    path('inventory/<int:pk>/', PharmacistInventoryDetailView.as_view(), name='pharmacist-inventory-detail'),
    path('medicines/', PharmacistMedicineCatalogView.as_view(), name='pharmacist-medicine-catalog'),
]
