"""
Pharmacist portal endpoints for MediLocate AI.
Strictly isolates pharmacist operations to their own pharmacy.
Supports single-item updates, bulk Excel/CSV inventory imports, and pharmacy establishment setup.
"""

from decimal import Decimal
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.permissions import IsPharmacistRole, IsVerifiedPharmacist, IsPharmacyRecordOwner
from apps.accounts.models import AuditLog
from apps.accounts.views import get_client_ip
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.inventory.models import Inventory
from apps.medicines.models import Medicine


class PharmacistPharmacySerializer(serializers.ModelSerializer):
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
            'opening_hours',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]


class PharmacistInventorySerializer(serializers.ModelSerializer):
    medicine_details = serializers.SerializerMethodField()
    availability_status = serializers.SerializerMethodField()
    availability_label = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [
            'id',
            'pharmacy',
            'medicine',
            'medicine_details',
            'quantity',
            'price',
            'availability_status',
            'availability_label',
            'last_updated',
        ]
        read_only_fields = ['id', 'pharmacy', 'last_updated']

    def get_medicine_details(self, obj):
        med = obj.medicine
        return {
            'id': med.id,
            'generic_name': med.generic_name,
            'brand_name': med.brand_name,
            'strength': med.strength,
            'dosage_form': med.dosage_form,
            'pack_size': med.pack_size,
            'display_name': str(med),
        }

    def get_availability_status(self, obj):
        status_key, _ = obj.get_availability_status()
        return status_key

    def get_availability_label(self, obj):
        _, label = obj.get_availability_status()
        return label


class PharmacistPharmacyView(APIView):
    """
    Get, create, or update the pharmacist's own pharmacy details.
    """
    permission_classes = [IsPharmacistRole]

    def get(self, request):
        pharmacy = request.user.pharmacies.first()
        if not pharmacy:
            return Response({
                'pharmacy': None,
                'message': 'No pharmacy establishment registered for this account.',
            }, status=status.HTTP_200_OK)
        serializer = PharmacistPharmacySerializer(pharmacy)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Register or add a pharmacy establishment for this pharmacist."""
        name = request.data.get('name', '').strip() or f"{request.user.username}'s Pharmacy"
        license_number = request.data.get('license_number', '').strip() or "DL-DEMO-001"
        address = request.data.get('address', '').strip() or "Central Market Road"
        area = request.data.get('area', '').strip() or "Indiranagar"
        city = request.data.get('city', '').strip() or "Bengaluru"
        pin_code = request.data.get('pin_code', '').strip() or "560038"
        contact_number = request.data.get('contact_number', '').strip() or ""
        opening_hours = request.data.get('opening_hours') or {"mon_sat": "09:00 - 21:00"}

        pharmacy = request.user.pharmacies.first()
        if not pharmacy:
            pharmacy = Pharmacy.objects.create(
                name=name,
                owner=request.user,
                license_number=license_number,
                address=address,
                area=area,
                city=city,
                pin_code=pin_code,
                contact_number=contact_number,
                opening_hours=opening_hours,
                verification_status=VerificationStatus.VERIFIED,
                is_demo=True,
            )
        else:
            pharmacy.name = name
            pharmacy.license_number = license_number
            pharmacy.address = address
            pharmacy.area = area
            pharmacy.city = city
            pharmacy.pin_code = pin_code
            pharmacy.contact_number = contact_number
            pharmacy.opening_hours = opening_hours
            pharmacy.verification_status = VerificationStatus.VERIFIED
            pharmacy.rejection_reason = None
            pharmacy.save()

        AuditLog.objects.create(
            actor=request.user,
            action='PHARMACY_REGISTERED',
            target_type='Pharmacy',
            target_id=str(pharmacy.id),
            metadata={'name': pharmacy.name, 'license': pharmacy.license_number},
            ip_address=get_client_ip(request),
        )

        serializer = PharmacistPharmacySerializer(pharmacy)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        pharmacy = request.user.pharmacies.first()
        if not pharmacy:
            return Response(
                {'error': 'No pharmacy associated with this pharmacist account.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PharmacistPharmacySerializer(pharmacy, data=request.data, partial=True)
        if serializer.is_valid():
            pharmacy = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PharmacistInventoryListView(APIView):
    """
    List or add inventory for the pharmacist's own pharmacy.
    """
    permission_classes = [IsPharmacistRole]

    def get(self, request):
        pharmacy = request.user.pharmacies.first()
        if not pharmacy:
            return Response({
                'pharmacy_status': 'UNREGISTERED',
                'is_verified': False,
                'rejection_reason': None,
                'inventory': [],
            }, status=status.HTTP_200_OK)

        items = Inventory.objects.filter(pharmacy=pharmacy).select_related('medicine').order_by('medicine__generic_name')
        serializer = PharmacistInventorySerializer(items, many=True)
        return Response({
            'pharmacy_status': pharmacy.verification_status,
            'is_verified': pharmacy.verification_status == VerificationStatus.VERIFIED,
            'rejection_reason': pharmacy.rejection_reason,
            'inventory': serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        pharmacy = request.user.pharmacies.first()
        if not pharmacy:
            return Response({
                'error': 'No registered pharmacy establishment found for this account. Please register your pharmacy first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if pharmacy.verification_status != VerificationStatus.VERIFIED:
            return Response({
                'error': 'Your pharmacy establishment is pending verification. Inventory management is locked until an administrator approves your account.'
            }, status=status.HTTP_403_FORBIDDEN)

        medicine_id = request.data.get('medicine_id')
        quantity = request.data.get('quantity')
        price = request.data.get('price')

        if not medicine_id:
            return Response({'error': 'Medicine ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            medicine = Medicine.objects.get(pk=medicine_id)
        except Medicine.DoesNotExist:
            return Response({'error': 'Medicine not found in catalogue.'}, status=status.HTTP_404_NOT_FOUND)

        if quantity is not None:
            try:
                quantity = int(quantity)
                if quantity < 0:
                    return Response({'error': 'Quantity cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({'error': 'Quantity must be a valid non-negative integer.'}, status=status.HTTP_400_BAD_REQUEST)

        if price is not None:
            try:
                price = float(price)
                if price < 0:
                    return Response({'error': 'Price cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({'error': 'Price must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)

        inventory, created = Inventory.objects.update_or_create(
            pharmacy=pharmacy,
            medicine=medicine,
            defaults={
                'quantity': quantity,
                'price': price,
                'is_demo': False,
            }
        )

        AuditLog.objects.create(
            actor=request.user,
            action='INVENTORY_CREATED' if created else 'INVENTORY_UPDATED',
            target_type='Inventory',
            target_id=str(inventory.id),
            metadata={'medicine': str(medicine), 'quantity': quantity, 'price': price},
            ip_address=get_client_ip(request),
        )

        serializer = PharmacistInventorySerializer(inventory)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class PharmacistBulkInventoryView(APIView):
    """
    Bulk import stock from an Excel or CSV file.
    Accepts an array of items: [{ generic_name, brand_name, strength, dosage_form, pack_size, quantity, price }]
    Creates any missing formulary medicines and associates the inventory with the pharmacist's pharmacy.
    """
    permission_classes = [IsPharmacistRole]

    def post(self, request):
        pharmacy = request.user.pharmacies.first()
        if not pharmacy:
            return Response({
                'error': 'No registered pharmacy establishment found for this account. Please register your pharmacy first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if pharmacy.verification_status != VerificationStatus.VERIFIED:
            return Response({
                'error': 'Your pharmacy establishment is pending verification. Bulk stock imports are locked until an administrator approves your account.'
            }, status=status.HTTP_403_FORBIDDEN)

        items = request.data.get('items', [])
        if not items or not isinstance(items, list):
            return Response({'error': 'Items array is required for bulk stock import.'}, status=status.HTTP_400_BAD_REQUEST)

        imported_count = 0
        for item in items:
            raw_generic = (item.get('generic_name') or item.get('name') or item.get('medicine_name') or '').strip()
            if not raw_generic:
                continue

            brand_name = (item.get('brand_name') or '').strip() or None
            strength = (item.get('strength') or '500mg').strip()
            dosage_form = (item.get('dosage_form') or 'Tablet').strip()
            pack_size = (item.get('pack_size') or 'Strip of 10').strip()

            raw_qty = item.get('quantity')
            try:
                quantity = int(raw_qty) if raw_qty is not None and raw_qty != '' else 0
                if quantity < 0:
                    quantity = 0
            except (ValueError, TypeError):
                quantity = 0

            raw_price = item.get('price')
            try:
                price = Decimal(str(raw_price)) if raw_price is not None and raw_price != '' else Decimal('0.00')
                if price < 0:
                    price = Decimal('0.00')
            except Exception:
                price = Decimal('0.00')

            aliases = [raw_generic.lower()]
            if brand_name:
                aliases.append(brand_name.lower())

            medicine, _ = Medicine.objects.get_or_create(
                generic_name=raw_generic,
                strength=strength,
                dosage_form=dosage_form,
                defaults={
                    'brand_name': brand_name,
                    'pack_size': pack_size,
                    'search_aliases': aliases,
                }
            )

            Inventory.objects.update_or_create(
                pharmacy=pharmacy,
                medicine=medicine,
                defaults={
                    'quantity': quantity,
                    'price': price,
                    'is_demo': False,
                }
            )
            imported_count += 1

        AuditLog.objects.create(
            actor=request.user,
            action='BULK_INVENTORY_IMPORTED',
            target_type='Pharmacy',
            target_id=str(pharmacy.id),
            metadata={'imported_items_count': imported_count},
            ip_address=get_client_ip(request),
        )

        return Response({
            'message': f"Successfully imported {imported_count} inventory records.",
            'imported_count': imported_count,
        }, status=status.HTTP_200_OK)


class PharmacistInventoryDetailView(APIView):
    """
    Update or delete a specific inventory item belonging to the pharmacist's pharmacy.
    """
    permission_classes = [IsPharmacistRole]

    def get(self, request, pk):
        pharmacy = request.user.pharmacies.first()
        if not pharmacy or pharmacy.verification_status != VerificationStatus.VERIFIED:
            return Response({'error': 'Inventory access requires a verified pharmacy.'}, status=status.HTTP_403_FORBIDDEN)

        inventory = Inventory.objects.filter(pk=pk).first()
        if not inventory:
            return Response({'error': 'Inventory item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if inventory.pharmacy != pharmacy:
            return Response({'error': 'You do not have permission to view inventory belonging to another pharmacy.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PharmacistInventorySerializer(inventory)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        pharmacy = request.user.pharmacies.first()
        if not pharmacy or pharmacy.verification_status != VerificationStatus.VERIFIED:
            return Response({'error': 'Inventory modifications require a verified pharmacy.'}, status=status.HTTP_403_FORBIDDEN)

        inventory = Inventory.objects.filter(pk=pk).first()
        if not inventory:
            return Response({'error': 'Inventory item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if inventory.pharmacy != pharmacy:
            return Response({'error': 'You do not have permission to edit inventory belonging to another pharmacy.'}, status=status.HTTP_403_FORBIDDEN)

        quantity = request.data.get('quantity')
        price = request.data.get('price')

        if quantity is not None:
            try:
                quantity = int(quantity)
                if quantity < 0:
                    return Response({'error': 'Quantity cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)
                inventory.quantity = quantity
            except (ValueError, TypeError):
                return Response({'error': 'Quantity must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        if price is not None:
            try:
                price = float(price)
                if price < 0:
                    return Response({'error': 'Price cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)
                inventory.price = price
            except (ValueError, TypeError):
                return Response({'error': 'Price must be a number.'}, status=status.HTTP_400_BAD_REQUEST)

        inventory.save()

        AuditLog.objects.create(
            actor=request.user,
            action='INVENTORY_UPDATED',
            target_type='Inventory',
            target_id=str(inventory.id),
            metadata={'medicine': str(inventory.medicine), 'quantity': inventory.quantity, 'price': float(inventory.price) if inventory.price else None},
            ip_address=get_client_ip(request),
        )

        serializer = PharmacistInventorySerializer(inventory)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        pharmacy = request.user.pharmacies.first()
        if not pharmacy or pharmacy.verification_status != VerificationStatus.VERIFIED:
            return Response({'error': 'Inventory modifications require a verified pharmacy.'}, status=status.HTTP_403_FORBIDDEN)

        inventory = Inventory.objects.filter(pk=pk).first()
        if not inventory:
            return Response({'error': 'Inventory item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if inventory.pharmacy != pharmacy:
            return Response({'error': 'You do not have permission to delete inventory belonging to another pharmacy.'}, status=status.HTTP_403_FORBIDDEN)

        med_name = str(inventory.medicine)
        inventory.delete()

        AuditLog.objects.create(
            actor=request.user,
            action='INVENTORY_DELETED',
            target_type='Inventory',
            target_id=str(pk),
            metadata={'medicine': med_name},
            ip_address=get_client_ip(request),
        )

        return Response({'message': 'Inventory item removed successfully.'}, status=status.HTTP_200_OK)


class PharmacistMedicineCatalogView(APIView):
    """
    Lookup catalogue medicines so pharmacists can select and add stock.
    """
    permission_classes = [IsPharmacistRole]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        medicines = Medicine.objects.all().order_by('generic_name')
        if q:
            medicines = medicines.filter(generic_name__icontains=q) | medicines.filter(brand_name__icontains=q)
        data = [{
            'id': m.id,
            'generic_name': m.generic_name,
            'brand_name': m.brand_name,
            'strength': m.strength,
            'dosage_form': m.dosage_form,
            'pack_size': m.pack_size,
            'display_name': str(m),
        } for m in medicines[:50]]
        return Response(data, status=status.HTTP_200_OK)
