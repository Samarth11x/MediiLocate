"""
Tests for seed_hosted_directory management command.
Validates:
- Execution without --confirm raises CommandError.
- Execution with --confirm seeds 20 verified pharmacies.
- NO User accounts or passwords are created.
- All pharmacies have owner=None and is_demo=True.
- Coordinates remain None (no distance fabrication).
- Command is idempotent (running twice does not duplicate).
"""

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth.models import User

from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.inventory.models import Inventory
from apps.medicines.models import Medicine


class SeedHostedDirectoryTests(TestCase):
    def test_requires_confirm_flag(self):
        """Must fail with CommandError if --confirm is not provided."""
        with self.assertRaises(CommandError) as ctx:
            call_command('seed_hosted_directory')
        self.assertIn("--confirm", str(ctx.exception))

    def test_seeds_safely_with_confirm(self):
        """Seeding must create 20 pharmacies with zero User accounts created."""
        initial_users = User.objects.count()

        call_command('seed_hosted_directory', confirm=True)

        # 1. Assert ZERO new users created
        self.assertEqual(User.objects.count(), initial_users)

        # 2. Assert exactly 20 primary pharmacies created
        pharmacies = Pharmacy.objects.filter(is_demo=True)
        self.assertEqual(pharmacies.count(), 20)

        for p in pharmacies:
            # Check invariants
            self.assertIsNone(p.owner)
            self.assertIsNone(p.latitude)
            self.assertIsNone(p.longitude)
            self.assertEqual(p.verification_status, VerificationStatus.VERIFIED)
            self.assertTrue(p.is_demo)

        # 3. Assert standard medicine formulary created
        crocin = Medicine.objects.filter(brand_name="Crocin", strength="500mg").first()
        self.assertIsNotNone(crocin)

        # 4. Assert inventory links created
        inv_count = Inventory.objects.filter(medicine=crocin).count()
        self.assertEqual(inv_count, 20)

        # 5. Assert idempotency
        call_command('seed_hosted_directory', confirm=True)
        self.assertEqual(Pharmacy.objects.filter(is_demo=True).count(), 20)
        self.assertEqual(Inventory.objects.filter(medicine=crocin).count(), 20)
        self.assertEqual(User.objects.count(), initial_users)
