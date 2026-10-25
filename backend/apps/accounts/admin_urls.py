"""
URL patterns for administrative portal endpoints in MediLocate AI.
"""

from django.urls import path
from .admin_views import (
    AdminOverviewView,
    AdminPharmacyListView,
    AdminPharmacyVerifyView,
    AdminMedicineListView,
    AdminMedicineDetailView,
    AdminUserListView,
    AdminAuditListView,
)

urlpatterns = [
    path('overview/', AdminOverviewView.as_view(), name='admin-overview'),
    path('pharmacies/', AdminPharmacyListView.as_view(), name='admin-pharmacy-list'),
    path('pharmacies/<int:pk>/verify/', AdminPharmacyVerifyView.as_view(), name='admin-pharmacy-verify'),
    path('medicines/', AdminMedicineListView.as_view(), name='admin-medicine-list'),
    path('medicines/<int:pk>/', AdminMedicineDetailView.as_view(), name='admin-medicine-detail'),
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('audit/', AdminAuditListView.as_view(), name='admin-audit-list'),
]
