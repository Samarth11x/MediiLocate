"""
Tests for role-based authentication and portal endpoints.
Covers:
- Registration (USER, PHARMACIST, role escalation rejection for ADMIN).
- Login, session restoration (/api/v1/auth/me/), logout.
- Pharmacist inventory isolation and verification gating.
- Admin portal permissions, pharmacy approvals/rejections, and audit logging.
"""

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


class AuthAndPortalTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Admin
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.local',
            password='Password123!'
        )
        UserProfile.objects.create(user=self.admin_user, role=UserRole.ADMIN)

        # Create Verified Pharmacist & Pharmacy
        self.verified_pharma_user = User.objects.create_user(
            username='pharma_verified',
            email='pharma1@test.local',
            password='Password123!'
        )
        UserProfile.objects.create(user=self.verified_pharma_user, role=UserRole.PHARMACIST)
        self.pharmacy_1 = Pharmacy.objects.create(
            name='Pharma One',
            owner=self.verified_pharma_user,
            address='123 Test St',
            area='South',
            city='TestCity',
            pin_code='560001',
            license_number='LIC-001',
            verification_status=VerificationStatus.VERIFIED,
            verified_by=self.admin_user
        )

        # Create Pending Pharmacist & Pharmacy
        self.pending_pharma_user = User.objects.create_user(
            username='pharma_pending',
            email='pharma2@test.local',
            password='Password123!'
        )
        UserProfile.objects.create(user=self.pending_pharma_user, role=UserRole.PHARMACIST)
        self.pharmacy_2 = Pharmacy.objects.create(
            name='Pharma Two Pending',
            owner=self.pending_pharma_user,
            address='456 Test St',
            area='North',
            city='TestCity',
            pin_code='560002',
            license_number='LIC-002',
            verification_status=VerificationStatus.PENDING
        )

        # Create Regular Patient
        self.patient_user = User.objects.create_user(
            username='patient_test',
            email='patient@test.local',
            password='Password123!'
        )
        UserProfile.objects.create(user=self.patient_user, role=UserRole.USER)

        # Create Test Medicine
        self.medicine = Medicine.objects.create(
            generic_name='Paracetamol',
            brand_name='Crocin',
            strength='500mg',
            dosage_form='Tablet',
            pack_size='Strip of 10'
        )

    # --------------------------------------------------------------------------
    # Authentication Tests
    # --------------------------------------------------------------------------

    def test_registration_user_success(self):
        """Standard patient registration creates active account with USER role."""
        url = reverse('auth-register')
        payload = {
            'username': 'new_patient',
            'email': 'new_patient@test.local',
            'password': 'SecurePassword123!',
            'role': 'USER',
            'phone_number': '+91 9988776655'
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['authenticated'])
        self.assertEqual(res.data['user']['role'], 'USER')

        # Check DB
        new_user = User.objects.get(username='new_patient')
        self.assertEqual(new_user.profile.role, UserRole.USER)

    def test_registration_pharmacist_creates_pending_pharmacy(self):
        """Pharmacist registration initializes establishment in PENDING state."""
        url = reverse('auth-register')
        payload = {
            'username': 'new_pharmacist',
            'email': 'new_pharma@test.local',
            'password': 'SecurePassword123!',
            'role': 'PHARMACIST',
            'pharmacy_name': 'New Hope Chemist',
            'license_number': 'LIC-999',
            'city': 'Bengaluru',
            'pin_code': '560034',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.get(username='new_pharmacist')
        self.assertEqual(new_user.profile.role, UserRole.PHARMACIST)
        pharmacy = new_user.pharmacies.first()
        self.assertIsNotNone(pharmacy)
        self.assertEqual(pharmacy.name, 'New Hope Chemist')
        self.assertEqual(pharmacy.verification_status, VerificationStatus.PENDING)

    def test_registration_strictly_blocks_admin_escalation(self):
        """Public registration cannot escalate to ADMIN."""
        url = reverse('auth-register')
        payload = {
            'username': 'fake_admin',
            'password': 'SecurePassword123!',
            'role': 'ADMIN'
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='fake_admin').exists())

    def test_login_and_session_restoration(self):
        """Login establishes authenticated session retrievable via /me/."""
        # 1. Initially unauthenticated
        me_url = reverse('auth-me')
        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['authenticated'])
        self.assertIsNone(res.data['user'])

        # 2. Login
        login_url = reverse('auth-login')
        res = self.client.post(login_url, {
            'username': 'patient_test',
            'password': 'Password123!'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['authenticated'])
        self.assertEqual(res.data['user']['username'], 'patient_test')

        # 3. Session restore
        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['authenticated'])
        self.assertEqual(res.data['user']['username'], 'patient_test')

        # 4. Logout
        logout_url = reverse('auth-logout')
        res = self.client.post(logout_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # 5. Verify unauthenticated again
        res = self.client.get(me_url)
        self.assertFalse(res.data['authenticated'])

    # --------------------------------------------------------------------------
    # Pharmacist Portal & Inventory Isolation Tests
    # --------------------------------------------------------------------------

    def test_verified_pharmacist_can_add_and_update_inventory(self):
        """Verified pharmacist can add stock to their own pharmacy."""
        self.client.force_login(self.verified_pharma_user)
        url = reverse('pharmacist-inventory-list')

        # Add stock
        payload = {
            'medicine_id': self.medicine.id,
            'quantity': 50,
            'price': 25.50
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['quantity'], 50)
        self.assertEqual(res.data['availability_status'], 'AVAILABLE')

        inv_id = res.data['id']

        # Update stock
        detail_url = reverse('pharmacist-inventory-detail', kwargs={'pk': inv_id})
        res = self.client.put(detail_url, {'quantity': 5, 'price': 26.00}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['quantity'], 5)
        self.assertEqual(res.data['availability_status'], 'LOW_STOCK')

    def test_pending_pharmacist_blocked_from_adding_inventory(self):
        """Pending pharmacist cannot add or modify inventory until approved."""
        self.client.force_login(self.pending_pharma_user)
        url = reverse('pharmacist-inventory-list')
        payload = {
            'medicine_id': self.medicine.id,
            'quantity': 20,
            'price': 15.00
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('pending verification', res.data['error'])

    def test_pharmacist_cannot_modify_another_pharmacys_inventory(self):
        """Pharmacist A cannot view, edit, or delete Pharmacist B's inventory item."""
        # Create inventory under pharmacy 1
        inv = Inventory.objects.create(
            pharmacy=self.pharmacy_1,
            medicine=self.medicine,
            quantity=30,
            price=20.00
        )

        # Login as pending pharma user (or another pharmacist)
        self.client.force_login(self.pending_pharma_user)
        detail_url = reverse('pharmacist-inventory-detail', kwargs={'pk': inv.id})

        # Attempt PUT
        res = self.client.put(detail_url, {'quantity': 999}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Attempt DELETE
        res = self.client.delete(detail_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Verify stock was untouched
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, 30)

    # --------------------------------------------------------------------------
    # Admin Portal & Audit Log Tests
    # --------------------------------------------------------------------------

    def test_non_admin_cannot_access_admin_overview(self):
        """Regular patient and pharmacist are rejected from admin APIs with 403."""
        self.client.force_login(self.patient_user)
        url = reverse('admin-overview')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_login(self.verified_pharma_user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_overview_and_verify_pharmacy(self):
        """Admin can review pending pharmacies, approve one, and trigger audit logging."""
        self.client.force_login(self.admin_user)

        # 1. Overview counts
        overview_url = reverse('admin-overview')
        res = self.client.get(overview_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data['total_users'], 3)
        self.assertEqual(res.data['pending_pharmacies'], 1)

        # 2. Approve pending pharmacy
        verify_url = reverse('admin-pharmacy-verify', kwargs={'pk': self.pharmacy_2.id})
        res = self.client.post(verify_url, {'action': 'approve'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.pharmacy_2.refresh_from_db()
        self.assertEqual(self.pharmacy_2.verification_status, VerificationStatus.VERIFIED)
        self.assertEqual(self.pharmacy_2.verified_by, self.admin_user)

        # 3. Verify audit log entry was created
        log = AuditLog.objects.filter(target_type='Pharmacy', target_id=str(self.pharmacy_2.id)).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, 'PHARMACY_VERIFIED')
        self.assertEqual(log.actor, self.admin_user)

    def test_admin_reject_pharmacy_requires_reason(self):
        """Admin rejection requires explicit rejection reason."""
        self.client.force_login(self.admin_user)
        verify_url = reverse('admin-pharmacy-verify', kwargs={'pk': self.pharmacy_2.id})

        # Rejection without reason fails
        res = self.client.post(verify_url, {'action': 'reject'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Rejection with reason succeeds
        res = self.client.post(verify_url, {
            'action': 'reject',
            'reason': 'Invalid drug license document uploaded.'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.pharmacy_2.refresh_from_db()
        self.assertEqual(self.pharmacy_2.verification_status, VerificationStatus.REJECTED)
        self.assertEqual(self.pharmacy_2.rejection_reason, 'Invalid drug license document uploaded.')

    # --------------------------------------------------------------------------
    # Phase 8 Security Hardening & Release Gate Tests
    # --------------------------------------------------------------------------

    def test_csrf_token_bootstrap_endpoint(self):
        """CSRF bootstrap endpoint returns csrfToken and sets csrftoken cookie."""
        url = reverse('auth-csrf')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('csrfToken', res.data)
        self.assertTrue(len(res.data['csrfToken']) > 0)
        self.assertIn('csrftoken', res.cookies)

    def test_csrf_enforcement_blocks_missing_or_invalid_token_on_mutations(self):
        """
        Session-authenticated unsafe requests (POST, PUT, DELETE) must fail with 403
        when CSRF token is missing or invalid.
        """
        csrf_client = APIClient(enforce_csrf_checks=True)
        login_url = reverse('auth-login')
        login_res = csrf_client.post(login_url, {
            'username': 'pharma_verified',
            'password': 'Password123!'
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

        inventory_url = reverse('pharmacist-inventory-list')
        payload = {
            'medicine_id': self.medicine.id,
            'quantity': 100,
            'price': 40.00
        }

        # 1. Missing CSRF token -> Rejected with 403 Forbidden
        res_no_csrf = csrf_client.post(inventory_url, payload, format='json')
        self.assertEqual(res_no_csrf.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Invalid CSRF token -> Rejected with 403 Forbidden
        res_bad_csrf = csrf_client.post(
            inventory_url,
            payload,
            format='json',
            HTTP_X_CSRFTOKEN='invalid_token_12345'
        )
        self.assertEqual(res_bad_csrf.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Retrieve valid CSRF token from bootstrap endpoint and supply HTTP_X_CSRFTOKEN
        csrf_res = csrf_client.get(reverse('auth-csrf'))
        self.assertEqual(csrf_res.status_code, status.HTTP_200_OK)
        valid_token = csrf_res.data['csrfToken']

        # 4. Valid CSRF token -> Request succeeds with 201 Created
        res_valid_csrf = csrf_client.post(
            inventory_url,
            payload,
            format='json',
            HTTP_X_CSRFTOKEN=valid_token
        )
        self.assertEqual(res_valid_csrf.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_valid_csrf.data['quantity'], 100)

        # 5. Safe GET request succeeds without explicit CSRF header
        res_get = csrf_client.get(inventory_url)
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)

    @override_settings(DJANGO_ENV='production', DEBUG=False)
    def test_seed_demo_users_strictly_refuses_production(self):
        """seed_demo_users must raise CommandError when DJANGO_ENV is production."""
        with self.assertRaises(CommandError) as ctx:
            call_command('seed_demo_users')
        self.assertIn("strictly prohibited in production", str(ctx.exception))

    @override_settings(DJANGO_ENV='development', DEBUG=False)
    def test_seed_demo_users_strictly_refuses_when_debug_is_false(self):
        """seed_demo_users must raise CommandError when DEBUG is False."""
        with self.assertRaises(CommandError) as ctx:
            call_command('seed_demo_users')
        self.assertIn("strictly prohibited in production", str(ctx.exception))

    def test_unauthenticated_requests_blocked_from_protected_endpoints(self):
        """Anonymous requests to pharmacist and admin endpoints receive 401 or 403."""
        res = self.client.get(reverse('pharmacist-inventory-list'))
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        res = self.client.post(reverse('pharmacist-inventory-list'), {'quantity': 10})
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        res = self.client.get(reverse('admin-overview'))
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_regular_user_blocked_from_pharmacist_and_admin_portals(self):
        """Patient role users receive 403 Forbidden on all pharmacist and admin endpoints."""
        self.client.force_login(self.patient_user)

        res = self.client.get(reverse('pharmacist-inventory-list'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.get(reverse('admin-overview'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_pharmacist_cannot_view_another_pharmacys_inventory_detail(self):
        """Pharmacist A receives 403 Forbidden when requesting Pharmacist B's inventory item detail."""
        inv = Inventory.objects.create(
            pharmacy=self.pharmacy_1,
            medicine=self.medicine,
            quantity=25,
            price=30.00
        )
        self.client.force_login(self.pending_pharma_user)
        detail_url = reverse('pharmacist-inventory-detail', kwargs={'pk': inv.id})

        res = self.client.get(detail_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejected_pharmacist_blocked_from_mutating_inventory(self):
        """Pharmacist whose pharmacy is rejected receives 403 Forbidden on inventory mutation."""
        self.pharmacy_2.verification_status = VerificationStatus.REJECTED
        self.pharmacy_2.rejection_reason = 'Invalid registration certificate'
        self.pharmacy_2.save()

        self.client.force_login(self.pending_pharma_user)
        res = self.client.post(reverse('pharmacist-inventory-list'), {
            'medicine_id': self.medicine.id,
            'quantity': 10
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
