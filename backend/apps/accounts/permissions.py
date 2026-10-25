"""
Role-based permission classes for MediLocate AI backend.
Enforces authorization boundaries server-side for Patient, Pharmacist, and Admin roles.
"""

from rest_framework import permissions
from .models import UserRole


class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to authenticated users who possess the ADMIN role,
    is_staff, or is_superuser flag.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.role == UserRole.ADMIN)


class IsPharmacistRole(permissions.BasePermission):
    """
    Allows access to authenticated users who possess the PHARMACIST role.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        profile = getattr(request.user, 'profile', None)
        return bool(profile and profile.role == UserRole.PHARMACIST)


class IsVerifiedPharmacist(permissions.BasePermission):
    """
    Allows mutation access only to pharmacists whose associated pharmacy
    establishment has been verified by an administrator.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        profile = getattr(request.user, 'profile', None)
        if not (profile and profile.role == UserRole.PHARMACIST):
            return False

        # Check if the user owns a verified pharmacy
        return request.user.pharmacies.filter(verification_status='VERIFIED').exists()


class IsPharmacyRecordOwner(permissions.BasePermission):
    """
    Object-level permission ensuring a pharmacist only modifies their own
    pharmacy or their own inventory records.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        # Admin users can access any record
        if request.user.is_staff or request.user.is_superuser:
            return True
        profile = getattr(request.user, 'profile', None)
        if profile and profile.role == UserRole.ADMIN:
            return True

        # Check for Pharmacy object
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        # Check for Inventory object
        if hasattr(obj, 'pharmacy') and hasattr(obj.pharmacy, 'owner'):
            return obj.pharmacy.owner == request.user

        return False
