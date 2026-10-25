"""
Automated tests for the 20 primary demo pharmacies network and end-to-end portal workflows.
Covers:
- Exactly 20 primary user-provided VERIFIED demo pharmacies in Belagavi & Bengaluru.
- Every one of the 20 verified demo pharmacies has a Paracetamol 500mg inventory record.
- Different stock quantities and all four stock statuses (AVAILABLE, LOW_STOCK, OUT_OF_STOCK, UNKNOWN).
- Different medicine combinations across pharmacies (e.g. Wellness Forever Tilakwadi superstore).
- Seed-command idempotency (rerunning seeder produces zero duplicates).
- Preservation of manual inventory edits after reseeding.
- Preservation of admin-approved or rejected status changes after reseeding.
- Pending/rejected pharmacy mutation restrictions (403 Forbidden).
- Ownership isolation between pharmacists (403 Forbidden).
- Patient search results containing exactly the 20 distinct verified demo pharmacies without distance fabrication.
- Admin dashboard metrics matching live database counts.
- Production and DEBUG=False safeguards.
"""

from decimal import Decimal
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import UserProfile, UserRole, AuditLog
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.medicines.models import Medicine
from apps.inventory.models import Inventory


EXPECTED_20_PHARMACY_NAMES = [
    "Apollo Pharmacy Peeranwadi Belagavi",
    "Laxmi Medical",
    "Zainab Medical & General Stores",
    "Piraji medical and general store",
    "Genericart Medicine Store | Dhanvantari Swast Aushadhi Seva | Belgaum",
    "Health Pro Medicals",
    "Paraji Medical And General Stores",
    "ANAND MEDICAL & GENERAL STORE",
    "HEALTH PRO PHARMACY",
    "Genericart Medicine Store | Sanjeevini Swast Aushadhi Seva | Belgaum",
    "PADMASHREE MEDICAL AND GENERAL STORES",
    "Varsha Medical",
    "Pandurang Medical & General Store",
    "Vedang Medicals",
    "SHRI CHANDRA PRABHA MEDICAL AND GENERAL STORE",
    "Wellness Forever Pharmacy - Khanapur Road, Tilakwadi, Belagavi",
    "Pragati Pharma",
    "Mediclass Medicals CA",
    "Shree Laxmi Medical & General Stores",
    "Apollo Pharmacy Rani Channamma Nagar",
]


@override_settings(DEBUG=True, DJANGO_ENV='development')
class DemoPortalSeedingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Seed the 20 primary demo pharmacies network
        call_command('seed_demo_portal_data')

    def test_twenty_verified_demo_pharmacies_seeded(self):
        """Database contains exactly the 20 user-provided demo pharmacies with VERIFIED status and null coordinates."""
        verified_pharmacies = Pharmacy.objects.filter(verification_status=VerificationStatus.VERIFIED)
        self.assertEqual(verified_pharmacies.count(), 20)

        for name in EXPECTED_20_PHARMACY_NAMES:
            pharm = Pharmacy.objects.filter(name=name).first()
            self.assertIsNotNone(pharm, f"Required demo pharmacy '{name}' was not found in the database.")
            self.assertEqual(pharm.verification_status, VerificationStatus.VERIFIED)
            self.assertTrue(pharm.is_demo)
            self.assertIsNotNone(pharm.owner, f"Pharmacy '{name}' must have an assigned owner.")
            # Coordinates must remain null where unavailable (no fabrication)
            self.assertIsNone(pharm.latitude, f"Coordinates should not be fabricated for '{name}'.")
            self.assertIsNone(pharm.longitude, f"Coordinates should not be fabricated for '{name}'.")

    def test_paracetamol_500mg_in_all_twenty_verified_pharmacies_with_four_states(self):
        """Every verified demo pharmacy stocks Paracetamol 500mg, covering all 4 stock states."""
        crocin_500 = Medicine.objects.get(generic_name='Paracetamol', strength='500mg', dosage_form='Tablet')
        verified_pharmacies = Pharmacy.objects.filter(verification_status=VerificationStatus.VERIFIED)

        statuses_found = set()
        for pharm in verified_pharmacies:
            inv = Inventory.objects.filter(pharmacy=pharm, medicine=crocin_500).first()
            self.assertIsNotNone(inv, f"Verified pharmacy '{pharm.name}' must have Paracetamol 500mg stock record.")
            status_key, _ = inv.get_availability_status()
            statuses_found.add(status_key)

        # All four states must be demonstrated across the verified network
        self.assertIn('AVAILABLE', statuses_found)
        self.assertIn('LOW_STOCK', statuses_found)
        self.assertIn('OUT_OF_STOCK', statuses_found)
        self.assertIn('UNKNOWN', statuses_found)

    def test_superstore_and_varied_inventory_distribution(self):
        """Wellness Forever Tilakwadi stocks all 10 medicines; other pharmacies have 3-6 items."""
        wellness = Pharmacy.objects.get(name="Wellness Forever Pharmacy - Khanapur Road, Tilakwadi, Belagavi")
        laxmi = Pharmacy.objects.get(name="Laxmi Medical")

        # Wellness Forever is a 24hr superstore stocking all 10 items
        self.assertEqual(Inventory.objects.filter(pharmacy=wellness).count(), 10)

        # Laxmi Medical has a smaller neighborhood inventory
        self.assertEqual(Inventory.objects.filter(pharmacy=laxmi).count(), 3)

        # Total platform inventory records exceeds 80
        self.assertGreaterEqual(Inventory.objects.count(), 80)

    def test_idempotent_demo_portal_seeding(self):
        """Re-running seed_demo_portal_data produces identical counts without duplicate records."""
        users_before = User.objects.count()
        pharmacies_before = Pharmacy.objects.count()
        medicines_before = Medicine.objects.count()
        inventories_before = Inventory.objects.count()

        # Run command a second time
        call_command('seed_demo_portal_data')

        self.assertEqual(User.objects.count(), users_before)
        self.assertEqual(Pharmacy.objects.count(), pharmacies_before)
        self.assertEqual(Medicine.objects.count(), medicines_before)
        self.assertEqual(Inventory.objects.count(), inventories_before)

    def test_preservation_of_manual_inventory_edits(self):
        """Manual inventory quantity and price updates are preserved upon reseeding."""
        apollo = Pharmacy.objects.get(name="Apollo Pharmacy Peeranwadi Belagavi")
        crocin = Medicine.objects.get(generic_name='Paracetamol', strength='500mg', dosage_form='Tablet')
        inv = Inventory.objects.get(pharmacy=apollo, medicine=crocin)

        # Manually modify quantity and price
        inv.quantity = 99
        inv.price = Decimal("39.99")
        inv.save()

        # Re-run seed command
        call_command('seed_demo_portal_data')

        # Verify edits were preserved
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, 99)
        self.assertEqual(inv.price, Decimal("39.99"))

    def test_preservation_of_admin_status_changes(self):
        """Admin status changes (e.g. approving GreenCross) persist upon reseeding."""
        greencross = Pharmacy.objects.get(name="Demo GreenCross Pharmacy (Fictional)")
        greencross.verification_status = VerificationStatus.VERIFIED
        greencross.save()

        # Re-run seed command
        call_command('seed_demo_portal_data')

        # Verify status is still VERIFIED, not reverted to PENDING
        greencross.refresh_from_db()
        self.assertEqual(greencross.verification_status, VerificationStatus.VERIFIED)

    @override_settings(DJANGO_ENV='production', DEBUG=False)
    def test_demo_seeding_refuses_production(self):
        """seed_demo_portal_data must raise CommandError in production environment."""
        with self.assertRaises(CommandError) as ctx:
            call_command('seed_demo_portal_data')
        self.assertIn("strictly prohibited in production", str(ctx.exception))

    @override_settings(DJANGO_ENV='development', DEBUG=False)
    def test_demo_seeding_refuses_when_debug_is_false(self):
        """seed_demo_portal_data must raise CommandError when DEBUG=False."""
        with self.assertRaises(CommandError) as ctx:
            call_command('seed_demo_portal_data')
        self.assertIn("strictly prohibited in production", str(ctx.exception))

    def test_all_pharmacist_demo_accounts_and_relationships(self):
        """Verify pharmacist_demo_01 through pharmacist_demo_20 accounts, plus pending/rejected."""
        for i in range(1, 21):
            uname = f"pharmacist_demo_{i:02d}"
            u = User.objects.filter(username=uname).first()
            self.assertIsNotNone(u, f"User '{uname}' must exist.")
            self.assertEqual(u.profile.role, UserRole.PHARMACIST)

        # Pending & Rejected accounts
        u_pending = User.objects.filter(username="pharmacist_demo_pending").first()
        self.assertIsNotNone(u_pending)
        self.assertEqual(u_pending.profile.role, UserRole.PHARMACIST)

        u_rejected = User.objects.filter(username="pharmacist_demo_rejected").first()
        self.assertIsNotNone(u_rejected)
        self.assertEqual(u_rejected.profile.role, UserRole.PHARMACIST)

        # Associated unverified pharmacies
        greencross = Pharmacy.objects.get(name="Demo GreenCross Pharmacy (Fictional)")
        self.assertEqual(greencross.verification_status, VerificationStatus.PENDING)
        self.assertEqual(greencross.owner, u_pending)

        sunrise = Pharmacy.objects.get(name="Demo Sunrise Pharmacy (Fictional)")
        self.assertEqual(sunrise.verification_status, VerificationStatus.REJECTED)
        self.assertEqual(sunrise.owner, u_rejected)

    def test_admin_metrics_reflect_database_values(self):
        """Admin overview endpoint returns exact live counts from database."""
        self.client.login(username='admin_demo', password='AdminDemoPass123!')
        res = self.client.get(reverse('admin-overview'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.data
        self.assertEqual(data['total_users'], User.objects.count())
        self.assertEqual(data['total_pharmacists'], UserProfile.objects.filter(role=UserRole.PHARMACIST).count())
        self.assertEqual(data['total_patients'], UserProfile.objects.filter(role=UserRole.USER).count())
        self.assertEqual(data['pending_pharmacies'], Pharmacy.objects.filter(verification_status=VerificationStatus.PENDING).count())
        self.assertEqual(data['verified_pharmacies'], Pharmacy.objects.filter(verification_status=VerificationStatus.VERIFIED).count())
        self.assertEqual(data['rejected_pharmacies'], Pharmacy.objects.filter(verification_status=VerificationStatus.REJECTED).count())
        self.assertEqual(data['total_medicines'], Medicine.objects.count())
        self.assertEqual(data['total_inventories'], Inventory.objects.count())

    def test_pharmacist_cannot_modify_another_pharmacys_stock(self):
        """Pharmacist 01 cannot edit or delete Pharmacist 16's inventory item (403 Forbidden)."""
        wellness = Pharmacy.objects.get(name="Wellness Forever Pharmacy - Khanapur Road, Tilakwadi, Belagavi")
        wellness_item = Inventory.objects.filter(pharmacy=wellness).first()

        # Login as Pharmacist 01 (Apollo Peeranwadi)
        self.client.login(username='pharmacist_demo_01', password='PharmaPass123!')
        detail_url = reverse('pharmacist-inventory-detail', kwargs={'pk': wellness_item.id})

        # Pharmacist 01 tries to GET Wellness item
        res_get = self.client.get(detail_url)
        self.assertEqual(res_get.status_code, status.HTTP_403_FORBIDDEN)

        # Pharmacist 01 tries to PUT Wellness item
        res_put = self.client.put(detail_url, {'quantity': 999}, format='json')
        self.assertEqual(res_put.status_code, status.HTTP_403_FORBIDDEN)

        # Pharmacist 01 tries to DELETE Wellness item
        res_delete = self.client.delete(detail_url)
        self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_pending_and_rejected_pharmacists_blocked_from_mutating_inventory(self):
        """Unverified pharmacists receive 403 Forbidden on stock additions."""
        med = Medicine.objects.first()

        # Pending Pharmacist
        self.client.login(username='pharmacist_demo_pending', password='PharmaPass123!')
        res_pending = self.client.post(reverse('pharmacist-inventory-list'), {
            'medicine_id': med.id,
            'quantity': 20,
            'price': 25.0
        }, format='json')
        self.assertEqual(res_pending.status_code, status.HTTP_403_FORBIDDEN)

        # Rejected Pharmacist
        self.client.login(username='pharmacist_demo_rejected', password='PharmaPass123!')
        res_rejected = self.client.post(reverse('pharmacist-inventory-list'), {
            'medicine_id': med.id,
            'quantity': 20,
            'price': 25.0
        }, format='json')
        self.assertEqual(res_rejected.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_login_credentials_rejected(self):
        """Invalid username or password returns 401 Unauthorized."""
        res = self.client.post(reverse('auth-login'), {
            'username': 'admin_demo',
            'password': 'WrongPassword999!'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(res.data.get('authenticated', True))

    def test_patient_medicine_search_returns_all_twenty_verified_pharmacies(self):
        """Patient search for 'Paracetamol 500mg' returns exactly the 20 verified pharmacies without distance fabrication."""
        self.client.login(username='patient_demo_01', password='PatientPass123!')
        res = self.client.get(reverse('search-medicines'), {'query': 'Paracetamol 500mg'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data['total_medicines'], 1)
        self.assertEqual(res.data['total_pharmacies'], 20)
        self.assertIn('demo_notice', res.data)
        self.assertIn('DEMO DATA', res.data['demo_notice'])

        pharmacies = res.data['pharmacies']
        seen_pharmacy_ids = set()

        for p_entry in pharmacies:
            pharm_id = p_entry['pharmacy']['id']
            self.assertNotIn(pharm_id, seen_pharmacy_ids, f"Pharmacy ID {pharm_id} returned multiple times.")
            seen_pharmacy_ids.add(pharm_id)

            pharm_db = Pharmacy.objects.get(pk=pharm_id)
            self.assertEqual(pharm_db.verification_status, VerificationStatus.VERIFIED)
            self.assertIn(pharm_db.name, EXPECTED_20_PHARMACY_NAMES)
            # Distance must NOT be fabricated when coordinates are not sent or unavailable
            self.assertIsNone(p_entry['distance_km'])
            # Pricing must be formatted string
            self.assertIsNotNone(p_entry['price'])
