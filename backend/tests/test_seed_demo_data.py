"""
Tests for seed_demo_data management command and seeded catalogue search verification.

Verifies:
- Creation of intended medicine, pharmacy, and inventory records.
- Idempotency (running multiple times creates zero duplicate records).
- MediBot medicine search integration with seeded database.
- Medication identity safeguards (strength mismatch exclusion).
- Truthful unavailable responses when catalogue is unpopulated.
- Priority of medical emergency interception with seeded data.
- Clear demonstration flagging on all demo pharmacies and inventory.
- Production environment safety refusal.
"""

from decimal import Decimal
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.medicines.models import Medicine
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.inventory.models import Inventory
from services.medibot_service import get_medibot_dialogue_manager


class SeedDemoDataCommandTests(TestCase):
    """Test suite verifying seed_demo_data management command and search accuracy."""

    def setUp(self):
        self.client = APIClient()
        self.chat_url = reverse("api-chat")

    def test_seed_command_creates_intended_records(self):
        """Management command successfully seeds medicines, pharmacies, and inventory."""
        self.assertEqual(Medicine.objects.count(), 0)
        self.assertEqual(Pharmacy.objects.count(), 0)
        self.assertEqual(Inventory.objects.count(), 0)

        call_command("seed_demo_data")

        self.assertEqual(Medicine.objects.count(), 10)
        self.assertEqual(Pharmacy.objects.count(), 4)
        self.assertEqual(Inventory.objects.count(), 10)

        # Verify Paracetamol 500mg presence
        pcm_500 = Medicine.objects.filter(
            generic_name="Paracetamol",
            strength="500mg",
            dosage_form="Tablet",
        ).first()
        self.assertIsNotNone(pcm_500)
        self.assertEqual(pcm_500.brand_name, "Crocin")
        self.assertIn("fever tablet", pcm_500.search_aliases)

        # Verify distinct strengths exist for safeguard testing
        pcm_650 = Medicine.objects.filter(
            generic_name="Paracetamol",
            strength="650mg",
            dosage_form="Tablet",
        ).first()
        self.assertIsNotNone(pcm_650)
        self.assertEqual(pcm_650.brand_name, "Dolo")

        # Verify syrup formulation exists
        pcm_syrup = Medicine.objects.filter(
            generic_name="Paracetamol",
            dosage_form="Syrup",
        ).first()
        self.assertIsNotNone(pcm_syrup)
        self.assertEqual(pcm_syrup.strength, "250mg/5ml")

    def test_seed_command_idempotency_no_duplicates(self):
        """Executing the seed command multiple times preserves records without duplicates."""
        call_command("seed_demo_data")
        initial_med_count = Medicine.objects.count()
        initial_pharm_count = Pharmacy.objects.count()
        initial_inv_count = Inventory.objects.count()

        # Run second time
        call_command("seed_demo_data")
        self.assertEqual(Medicine.objects.count(), initial_med_count)
        self.assertEqual(Pharmacy.objects.count(), initial_pharm_count)
        self.assertEqual(Inventory.objects.count(), initial_inv_count)

        # Run third time
        call_command("seed_demo_data")
        self.assertEqual(Medicine.objects.count(), initial_med_count)
        self.assertEqual(Pharmacy.objects.count(), initial_pharm_count)
        self.assertEqual(Inventory.objects.count(), initial_inv_count)

    def test_search_finds_seeded_paracetamol_500mg(self):
        """Searching for 'Find Paracetamol 500mg' finds the seeded catalogue entry."""
        call_command("seed_demo_data")

        response = self.client.post(
            self.chat_url,
            {"message": "Find Paracetamol 500mg"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(data["intent"], "MEDICINE_SEARCH")
        self.assertGreaterEqual(len(data["results"]), 1)

        first_match = data["results"][0]
        self.assertEqual(first_match["medicine"]["generic_name"], "Paracetamol")
        self.assertEqual(first_match["medicine"]["strength"], "500mg")
        self.assertEqual(first_match["medicine"]["dosage_form"], "Tablet")
        self.assertEqual(first_match["medicine"]["brand_name"], "Crocin")

    def test_strength_mismatch_safeguard_enforced(self):
        """Searching for Paracetamol 500mg strictly excludes 650mg and 250mg formulations."""
        call_command("seed_demo_data")

        # 1. Search for 500mg -> must only return 500mg
        res_500 = self.client.post(
            self.chat_url,
            {"message": "Find Paracetamol 500mg"},
            format="json",
        )
        data_500 = res_500.json()
        self.assertEqual(len(data_500["results"]), 1)
        self.assertEqual(data_500["results"][0]["medicine"]["strength"], "500mg")
        self.assertEqual(data_500["results"][0]["medicine"]["brand_name"], "Crocin")

        # 2. Search for 650mg -> must only return 650mg (Dolo)
        res_650 = self.client.post(
            self.chat_url,
            {"message": "Find Paracetamol 650mg"},
            format="json",
        )
        data_650 = res_650.json()
        self.assertEqual(len(data_650["results"]), 1)
        self.assertEqual(data_650["results"][0]["medicine"]["strength"], "650mg")
        self.assertEqual(data_650["results"][0]["medicine"]["brand_name"], "Dolo")

        # 3. Search for non-existent strength (1000mg) -> returns no results, never substitutes 500mg or 650mg
        res_1000 = self.client.post(
            self.chat_url,
            {"message": "Find Paracetamol 1000mg"},
            format="json",
        )
        data_1000 = res_1000.json()
        self.assertEqual(data_1000["status"], "no_results")
        self.assertEqual(len(data_1000["results"]), 0)

    def test_dosage_form_mismatch_safeguard_enforced(self):
        """Searching for Paracetamol Syrup strictly returns Syrup, excluding Tablets."""
        call_command("seed_demo_data")

        response = self.client.post(
            self.chat_url,
            {"message": "Find Paracetamol Syrup"},
            format="json",
        )
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["medicine"]["dosage_form"], "Syrup")
        self.assertEqual(data["results"][0]["medicine"]["brand_name"], "Calpol")

    def test_empty_catalogue_returns_truthful_unavailable_response(self):
        """With an empty database, MediBot honestly reports catalogue as unpopulated."""
        self.assertEqual(Medicine.objects.count(), 0)

        response = self.client.post(
            self.chat_url,
            {"message": "Find Paracetamol 500mg"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["status"], "unavailable")
        self.assertEqual(len(data["results"]), 0)
        self.assertIn("unpopulated", data["message"].lower())

    def test_emergency_detection_preempts_with_seeded_data(self):
        """Acute medical emergencies take precedence over medicine search regardless of catalog data."""
        call_command("seed_demo_data")

        response = self.client.post(
            self.chat_url,
            {"message": "I have severe chest pain and difficulty breathing, find paracetamol"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["intent"], "EMERGENCY_CONCERN")
        self.assertEqual(data["status"], "safety_response")
        self.assertEqual(data["safety_category"], "emergency_concern")
        self.assertIn("112", data["message"])
        self.assertIn("108", data["message"])
        self.assertIn("911", data["message"])
        self.assertEqual(len(data["results"]), 0)

    def test_demo_data_flagging_prevents_mistaken_live_inventory(self):
        """All seeded records are strictly flagged as demo and clearly labeled as fictional."""
        call_command("seed_demo_data")

        # Check all pharmacies are flagged demo and contain fictional marker in name
        for pharmacy in Pharmacy.objects.all():
            self.assertTrue(pharmacy.is_demo)
            self.assertIn("Fictional Dev", pharmacy.name)

        # Check all inventory records are flagged demo
        for inv in Inventory.objects.all():
            self.assertTrue(inv.is_demo)

        # Verify chat endpoint returns demo_notice: true
        response = self.client.post(
            self.chat_url,
            {"message": "Find Paracetamol 500mg"},
            format="json",
        )
        data = response.json()
        self.assertTrue(data["demo_notice"])

    @override_settings(DJANGO_ENV="production")
    def test_seed_command_refuses_production_environment(self):
        """Command raises CommandError if executed when DJANGO_ENV is 'production'."""
        with self.assertRaises(CommandError) as ctx:
            call_command("seed_demo_data")
        self.assertIn("production", str(ctx.exception).lower())
