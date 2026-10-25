"""
Administrative endpoints for MediLocate AI.
Guarded by IsAdminUserRole permission.
Provides metrics, pharmacy verification workflows, catalogue management, and audit logging.
"""

from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import UserProfile, UserRole, AuditLog
from .permissions import IsAdminUserRole
from .views import get_client_ip
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.medicines.models import Medicine
from apps.inventory.models import Inventory


class AdminPharmacySerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    verified_by_username = serializers.CharField(source='verified_by.username', read_only=True)

    class Meta:
        model = Pharmacy
        fields = [
            'id',
            'name',
            'address',
            'area',
            'city',
            'pin_code',
            'contact_number',
            'license_number',
            'verification_status',
            'rejection_reason',
            'owner',
            'owner_username',
            'owner_email',
            'verified_by',
            'verified_by_username',
            'verified_at',
            'is_demo',
            'created_at',
        ]
        read_only_fields = fields


class AdminMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = [
            'id',
            'generic_name',
            'brand_name',
            'strength',
            'dosage_form',
            'pack_size',
            'search_aliases',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    pharmacy_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'phone_number',
            'pharmacy_name',
            'is_active',
            'is_staff',
            'date_joined',
        ]
        read_only_fields = fields

    def get_role(self, obj):
        profile = getattr(obj, 'profile', None)
        if obj.is_superuser or obj.is_staff:
            return 'ADMIN'
        return profile.role if profile else 'USER'

    def get_phone_number(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.phone_number if profile else None

    def get_pharmacy_name(self, obj):
        pharmacy = obj.pharmacies.first()
        return pharmacy.name if pharmacy else None


class AdminOverviewView(APIView):
    """
    Live platform overview counts for the admin dashboard.
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        total_users = User.objects.count()
        total_pharmacists = UserProfile.objects.filter(role=UserRole.PHARMACIST).count()
        total_patients = UserProfile.objects.filter(role=UserRole.USER).count()
        pending_pharmacies = Pharmacy.objects.filter(verification_status=VerificationStatus.PENDING).count()
        verified_pharmacies = Pharmacy.objects.filter(verification_status=VerificationStatus.VERIFIED).count()
        rejected_pharmacies = Pharmacy.objects.filter(verification_status=VerificationStatus.REJECTED).count()
        total_medicines = Medicine.objects.count()
        total_inventories = Inventory.objects.count()
        recent_audits = AuditLog.objects.count()

        return Response({
            'total_users': total_users,
            'total_pharmacists': total_pharmacists,
            'total_patients': total_patients,
            'pending_pharmacies': pending_pharmacies,
            'verified_pharmacies': verified_pharmacies,
            'rejected_pharmacies': rejected_pharmacies,
            'total_medicines': total_medicines,
            'total_inventories': total_inventories,
            'recent_audits': recent_audits,
        }, status=status.HTTP_200_OK)


class AdminPharmacyListView(APIView):
    """
    Lists pharmacy establishments with optional status filtering.
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        qs = Pharmacy.objects.select_related('owner', 'verified_by').order_by('-created_at')
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(verification_status=status_filter.upper())

        serializer = AdminPharmacySerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPharmacyVerifyView(APIView):
    """
    Approve or reject a pharmacy establishment.
    Enforces audit logging on every verification action.
    """
    permission_classes = [IsAdminUserRole]

    def post(self, request, pk):
        try:
            pharmacy = Pharmacy.objects.get(pk=pk)
        except Pharmacy.DoesNotExist:
            return Response({'error': 'Pharmacy not found.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        reason = request.data.get('reason', '').strip()

        if action not in ['approve', 'reject']:
            return Response(
                {'error': "Invalid action. Must be 'approve' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == 'reject' and not reason:
            return Response(
                {'error': "A rejection reason is required when rejecting a pharmacy."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == 'approve':
            pharmacy.verification_status = VerificationStatus.VERIFIED
            pharmacy.rejection_reason = None
            log_action = 'PHARMACY_VERIFIED'
        else:
            pharmacy.verification_status = VerificationStatus.REJECTED
            pharmacy.rejection_reason = reason
            log_action = 'PHARMACY_REJECTED'

        pharmacy.verified_by = request.user
        pharmacy.verified_at = timezone.now()
        pharmacy.save()

        # Audit log entry
        AuditLog.objects.create(
            actor=request.user,
            action=log_action,
            target_type='Pharmacy',
            target_id=str(pharmacy.id),
            metadata={
                'pharmacy_name': pharmacy.name,
                'owner_username': pharmacy.owner.username if pharmacy.owner else None,
                'status': pharmacy.verification_status,
                'reason': reason if action == 'reject' else None,
            },
            ip_address=get_client_ip(request),
        )

        return Response({
            'message': f"Pharmacy successfully {pharmacy.verification_status.lower()}.",
            'pharmacy': AdminPharmacySerializer(pharmacy).data,
        }, status=status.HTTP_200_OK)


class AdminMedicineListView(APIView):
    """
    Lists catalogue medicines and creates new ones.
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        medicines = Medicine.objects.all().order_by('generic_name')
        q = request.query_params.get('q')
        if q:
            medicines = medicines.filter(generic_name__icontains=q) | medicines.filter(brand_name__icontains=q)
        serializer = AdminMedicineSerializer(medicines[:100], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AdminMedicineSerializer(data=request.data)
        if serializer.is_valid():
            medicine = serializer.save()
            AuditLog.objects.create(
                actor=request.user,
                action='MEDICINE_CREATED',
                target_type='Medicine',
                target_id=str(medicine.id),
                metadata={'generic_name': medicine.generic_name, 'brand_name': medicine.brand_name},
                ip_address=get_client_ip(request),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AdminMedicineDetailView(APIView):
    """
    Retrieve, update, or remove a medicine record.
    """
    permission_classes = [IsAdminUserRole]

    def put(self, request, pk):
        try:
            medicine = Medicine.objects.get(pk=pk)
        except Medicine.DoesNotExist:
            return Response({'error': 'Medicine not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminMedicineSerializer(medicine, data=request.data, partial=True)
        if serializer.is_valid():
            medicine = serializer.save()
            AuditLog.objects.create(
                actor=request.user,
                action='MEDICINE_UPDATED',
                target_type='Medicine',
                target_id=str(medicine.id),
                metadata={'generic_name': medicine.generic_name, 'brand_name': medicine.brand_name},
                ip_address=get_client_ip(request),
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            medicine = Medicine.objects.get(pk=pk)
        except Medicine.DoesNotExist:
            return Response({'error': 'Medicine not found.'}, status=status.HTTP_404_NOT_FOUND)

        med_name = f"{medicine.generic_name} ({medicine.brand_name or ''})"
        medicine.delete()
        AuditLog.objects.create(
            actor=request.user,
            action='MEDICINE_DELETED',
            target_type='Medicine',
            target_id=str(pk),
            metadata={'name': med_name},
            ip_address=get_client_ip(request),
        )
        return Response({'message': 'Medicine deleted.'}, status=status.HTTP_200_OK)


class AdminUserListView(APIView):
    """
    Lists registered users and their roles without leaking password hashes.
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        users = User.objects.select_related('profile').prefetch_related('pharmacies').order_by('-date_joined')
        serializer = AdminUserSerializer(users[:200], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminAuditListView(APIView):
    """
    Lists recent audit logs for administrative tracking.
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        logs = AuditLog.objects.select_related('actor').order_by('-timestamp')[:100]
        from .serializers import AuditLogSerializer
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
