"""
URL routes for search domain application.
"""

from django.urls import path
from apps.search.views import MedicineSearchView, PharmacySearchView

urlpatterns = [
    path('medicines/', MedicineSearchView.as_view(), name='search-medicines'),
    path('pharmacies/', PharmacySearchView.as_view(), name='search-pharmacies'),
]
