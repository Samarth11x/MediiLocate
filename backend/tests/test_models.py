"""
Model tests for MediLocate AI (Pharmacy, Medicine, and Inventory).
"""

from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.medicines.models import Medicine
from apps.inventory.models import Inventory

class PharmacyModelTests(TestCase):
    def test_pharmacy_creation_and_defaults(self):
        """Verify successful pharmacy creation with expected defaults."""
        pharmacy = Pharmacy.objects.create(
            name="Apex Care Pharmacy",
            address="102 Healthcare Boulevard",
            area="Koramangala",
            city="Bengaluru",
            pin_code="560034",
            latitude=Decimal("12.935200"),
            longitude=Decimal("77.624500"),
            contact_number="+91 98765 43210",
        )
        self.assertEqual(pharmacy.verification_status, VerificationStatus.PENDING)
        self.assertTrue(pharmacy.is_demo)
        self.assertEqual(str(pharmacy), "Apex Care Pharmacy (Koramangala, Bengaluru)")

    def test_coordinate_validation_valid(self):
        """Valid WGS84 coordinates pass validation."""
        pharmacy = Pharmacy(
            name="Valid Geo Pharmacy",
            address="Street 1",
            area="Indiranagar",
            city="Bengaluru",
            pin_code="560038",
            latitude=Decimal("12.971600"),
            longitude=Decimal("77.594600"),
        )
        # Should not raise
        pharmacy.full_clean()

    def test_coordinate_validation_invalid_latitude(self):
        """Latitude outside [-90.0, 90.0] raises ValidationError."""
        pharmacy_high = Pharmacy(
            name="Invalid Lat Pharmacy",
            address="Street 1",
            area="Indiranagar",
            city="Bengaluru",
            pin_code="560038",
            latitude=Decimal("91.500000"),
            longitude=Decimal("77.594600"),
        )
        with self.assertRaises(ValidationError):
            pharmacy_high.full_clean()

        pharmacy_low = Pharmacy(
            name="Invalid Lat Pharmacy Low",
            address="Street 1",
            area="Indiranagar",
            city="Bengaluru",
            pin_code="560038",
            latitude=Decimal("-95.000000"),
            longitude=Decimal("77.594600"),
        )
        with self.assertRaises(ValidationError):
            pharmacy_low.full_clean()

    def test_coordinate_validation_invalid_longitude(self):
        """Longitude outside [-180.0, 180.0] raises ValidationError."""
        pharmacy_high = Pharmacy(
            name="Invalid Lon Pharmacy",
            address="Street 1",
            area="Indiranagar",
            city="Bengaluru",
            pin_code="560038",
            latitude=Decimal("12.971600"),
            longitude=Decimal("185.000000"),
        )
        with self.assertRaises(ValidationError):
            pharmacy_high.full_clean()


class MedicineModelTests(TestCase):
    def test_medicine_creation(self):
        """Verify successful medicine formulary record creation."""
        medicine = Medicine.objects.create(
            generic_name="Amoxicillin",
            brand_name="Mox 500",
            strength="500mg",
            dosage_form="Capsule",
            pack_size="Strip of 10",
            search_aliases=["Amox", "Amoxycillin"],
        )
        self.assertEqual(str(medicine), "Mox 500 (Amoxicillin) 500mg Capsule")

    def test_medicine_without_brand_name(self):
        """Medicine with only generic name string formats correctly."""
        medicine = Medicine.objects.create(
            generic_name="Paracetamol",
            strength="650mg",
            dosage_form="Tablet",
        )
        self.assertEqual(str(medicine), "Paracetamol 650mg Tablet")


class InventoryModelTests(TestCase):
    def setUp(self):
        self.pharmacy = Pharmacy.objects.create(
            name="Care Plus Pharmacy",
            address="45 Central Road",
            area="Jayanagar",
            city="Bengaluru",
            pin_code="560011",
        )
        self.medicine = Medicine.objects.create(
            generic_name="Paracetamol",
            brand_name="Dolo 650",
            strength="650mg",
            dosage_form="Tablet",
        )

    def test_inventory_creation_and_relationships(self):
        """Verify inventory links pharmacy and medicine properly with foreign keys."""
        inventory = Inventory.objects.create(
            pharmacy=self.pharmacy,
            medicine=self.medicine,
            quantity=50,
            price=Decimal("32.50"),
        )
        self.assertEqual(inventory.pharmacy, self.pharmacy)
        self.assertEqual(inventory.medicine, self.medicine)
        self.assertIn(inventory, self.pharmacy.inventory_records.all())
        self.assertIn(inventory, self.medicine.inventory_records.all())

    def test_unique_pharmacy_medicine_inventory_constraint(self):
        """A pharmacy cannot have duplicate inventory entries for the same medicine."""
        Inventory.objects.create(
            pharmacy=self.pharmacy,
            medicine=self.medicine,
            quantity=20,
            price=Decimal("30.00"),
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Inventory.objects.create(
                    pharmacy=self.pharmacy,
                    medicine=self.medicine,
                    quantity=10,
                    price=Decimal("30.00"),
                )

    def test_negative_quantity_rejection(self):
        """Inventory with negative quantity fails validation."""
        inventory = Inventory(
            pharmacy=self.pharmacy,
            medicine=self.medicine,
            quantity=-5,
        )
        with self.assertRaises(ValidationError):
            inventory.full_clean()

    def test_negative_price_rejection(self):
        """Inventory with negative price fails validation."""
        inventory = Inventory(
            pharmacy=self.pharmacy,
            medicine=self.medicine,
            quantity=10,
            price=Decimal("-15.00"),
        )
        with self.assertRaises(ValidationError):
            inventory.full_clean()

    def test_null_quantity_distinct_from_zero(self):
        """
        Quantity NULL represents unknown stock, whereas 0 represents confirmed out-of-stock.
        They must remain distinct and map to distinct availability interpretations.
        """
        inv_unknown = Inventory.objects.create(
            pharmacy=self.pharmacy,
            medicine=self.medicine,
            quantity=None,
        )
        self.assertIsNone(inv_unknown.quantity)
        status_key, status_label = inv_unknown.get_availability_status()
        self.assertEqual(status_key, "UNKNOWN")
        self.assertEqual(status_label, "Availability Unknown")

        # Update to confirmed 0
        inv_unknown.quantity = 0
        inv_unknown.save()
        self.assertEqual(inv_unknown.quantity, 0)
        self.assertIsNotNone(inv_unknown.quantity)
        status_key_zero, status_label_zero = inv_unknown.get_availability_status()
        self.assertEqual(status_key_zero, "OUT_OF_STOCK")
        self.assertEqual(status_label_zero, "Out of Stock")

    def test_availability_threshold_classification(self):
        """Verify calculated availability states based on quantity."""
        inv = Inventory(pharmacy=self.pharmacy, medicine=self.medicine)

        # Low stock (< 10)
        inv.quantity = 5
        self.assertEqual(inv.get_availability_status(low_stock_threshold=10)[0], "LOW_STOCK")

        # Available (>= 10)
        inv.quantity = 15
        self.assertEqual(inv.get_availability_status(low_stock_threshold=10)[0], "AVAILABLE")
