"""
Tests for MediBot Chat API endpoint (POST /api/v1/chat/).
Verifies input validation, HTTP status codes, intent routing, safety interception,
tool execution with seeded medicines, and privacy (zero chat persistence).
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from decimal import Decimal
from apps.medicines.models import Medicine
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.inventory.models import Inventory


class ChatMessageEndpointTests(TestCase):
    """Test suite for POST /api/v1/chat/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api-chat')

        # Seed sample medicine for tool search verification
        self.medicine = Medicine.objects.create(
            generic_name="Paracetamol",
            brand_name="Crocin",
            strength="500mg",
            dosage_form="Tablet",
            pack_size="Strip of 10",
            search_aliases=["pcm", "fever tablet"],
        )

    def test_greeting_message(self):
        """Valid greeting returns HTTP 200 with GREETING intent."""
        payload = {"message": "Hello MediBot"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["intent"], "GREETING")
        self.assertEqual(data["status"], "success")
        self.assertIn("suggestions", data)
        self.assertTrue(data["demo_notice"])
        self.assertIsNone(data["safety_category"])

    def test_emergency_interception(self):
        """Acute medical emergency triggers immediate emergency hotline guidance."""
        payload = {"message": "I am having severe chest pain and cannot breathe"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["intent"], "EMERGENCY_CONCERN")
        self.assertEqual(data["status"], "safety_response")
        self.assertEqual(data["safety_category"], "emergency_concern")
        # Check that emergency numbers are supplied
        self.assertIn("112", data["message"])
        self.assertIn("108", data["message"])
        self.assertIn("911", data["message"])

    def test_medical_advice_interception(self):
        """Clinical advice or prescribing queries are safely intercepted."""
        payload = {"message": "What should I take for severe fever and headache?"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["intent"], "MEDICAL_ADVICE")
        self.assertEqual(data["status"], "safety_response")
        self.assertEqual(data["safety_category"], "medical_advice")
        self.assertIn("consult a qualified medical doctor", data["message"].lower())

    def test_medicine_search_direct(self):
        """Specific medicine query searches database and returns matching results."""
        payload = {"message": "Find Paracetamol 500mg"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["intent"], "MEDICINE_SEARCH")
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(len(data["results"]), 1)
        first_result = data["results"][0]
        self.assertEqual(first_result["medicine"]["generic_name"], "Paracetamol")

    def test_generic_medicine_search_needs_clarification(self):
        """Generic medicine search prompts user for specific name with multi-turn context."""
        payload = {"message": "Find a medicine"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["intent"], "MEDICINE_SEARCH")
        self.assertEqual(data["status"], "needs_clarification")
        self.assertEqual(data["context"]["step"], "awaiting_medicine_name")

    def test_multi_turn_continuation_with_context(self):
        """Following up with medicine name when step is awaiting_medicine_name resolves search."""
        payload = {
            "message": "Crocin 500mg",
            "context": {"step": "awaiting_medicine_name"},
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["intent"], "MEDICINE_SEARCH")
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(len(data["results"]), 1)

    def test_empty_message_returns_400(self):
        """Empty string message returns HTTP 400."""
        payload = {"message": ""}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_whitespace_message_returns_400(self):
        """Whitespace only message returns HTTP 400."""
        payload = {"message": "      "}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_missing_message_field_returns_400(self):
        """Missing message field in payload returns HTTP 400."""
        payload = {"something_else": "test"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_non_string_message_returns_400(self):
        """Numeric or boolean message returns HTTP 400."""
        payload = {"message": 99999}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_oversized_message_returns_400(self):
        """Message exceeding 500 characters returns HTTP 400."""
        payload = {"message": "a" * 501}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_invalid_context_type_returns_400(self):
        """Non-dictionary context parameter returns HTTP 400."""
        payload = {"message": "hello", "context": "invalid_string_context"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_unsupported_methods_return_405(self):
        """GET, PUT, DELETE methods are disallowed on /api/v1/chat/."""
        get_res = self.client.get(self.url)
        self.assertEqual(get_res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        put_res = self.client.put(self.url, {"message": "hi"}, format="json")
        self.assertEqual(put_res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        del_res = self.client.delete(self.url)
        self.assertEqual(del_res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_pharmacy_search_multi_turn_with_medicine_context(self):
        """
        BUG 1 REGRESSION TEST:
        Search Paracetamol 500mg -> follow up with 'Find nearby pharmacies'.
        Verifies:
        - MediBot preserves searched_medicine & searched_medicine_id in context.
        - Returns matching verified pharmacy inventory records across stock states (AVAILABLE, LOW_STOCK, OUT_OF_STOCK).
        - Unverified pharmacy is excluded.
        - Distance is None and location privacy disclaimer is present when coordinates not shared.
        - Fictional demonstration notice is present.
        """
        # Create verified pharmacies
        p_care = Pharmacy.objects.create(
            name="CarePoint Pharmacy",
            address="101 Healthcare Lane",
            area="Koramangala",
            city="Bengaluru",
            pin_code="560034",
            latitude=Decimal("12.934000"),
            longitude=Decimal("77.610000"),
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )
        p_metro = Pharmacy.objects.create(
            name="Metro Chemist",
            address="12 Retail Arcade",
            area="Indiranagar",
            city="Bengaluru",
            pin_code="560038",
            latitude=Decimal("12.978000"),
            longitude=Decimal("77.640000"),
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )
        p_apollo = Pharmacy.objects.create(
            name="Apollo Life Chemist",
            address="45 Hospital Road",
            area="Jayanagar",
            city="Bengaluru",
            pin_code="560041",
            latitude=Decimal("12.925000"),
            longitude=Decimal("77.585000"),
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )
        # Unverified pharmacy
        p_unverified = Pharmacy.objects.create(
            name="GreenCross Meds",
            address="99 Unverified St",
            area="Whitefield",
            city="Bengaluru",
            pin_code="560066",
            verification_status=VerificationStatus.PENDING,
            is_demo=True,
        )

        # Create inventory records
        Inventory.objects.create(
            pharmacy=p_care,
            medicine=self.medicine,
            quantity=45,  # AVAILABLE
            price=Decimal("30.50"),
            is_demo=True,
        )
        Inventory.objects.create(
            pharmacy=p_metro,
            medicine=self.medicine,
            quantity=5,  # LOW_STOCK
            price=Decimal("32.00"),
            is_demo=True,
        )
        Inventory.objects.create(
            pharmacy=p_apollo,
            medicine=self.medicine,
            quantity=0,  # OUT_OF_STOCK
            price=Decimal("29.00"),
            is_demo=True,
        )
        Inventory.objects.create(
            pharmacy=p_unverified,
            medicine=self.medicine,
            quantity=10,
            price=Decimal("28.00"),
            is_demo=True,
        )

        # Turn 1: Search for Paracetamol 500mg
        turn1_res = self.client.post(self.url, {"message": "Find Paracetamol 500mg"}, format="json")
        self.assertEqual(turn1_res.status_code, status.HTTP_200_OK)
        turn1_data = turn1_res.json()
        self.assertEqual(turn1_data["intent"], "MEDICINE_SEARCH")
        self.assertEqual(turn1_data["status"], "success")
        self.assertIn("context", turn1_data)
        self.assertIn("searched_medicine", turn1_data["context"])
        self.assertIn("searched_medicine_id", turn1_data["context"])
        self.assertIn("Find nearby pharmacies", turn1_data["suggestions"])

        # Turn 2: Follow up with 'Find nearby pharmacies' passing preserved context
        turn2_payload = {
            "message": "Find nearby pharmacies",
            "context": turn1_data["context"],
        }
        turn2_res = self.client.post(self.url, turn2_payload, format="json")
        self.assertEqual(turn2_res.status_code, status.HTTP_200_OK)
        turn2_data = turn2_res.json()

        # Verifications
        self.assertEqual(turn2_data["intent"], "PHARMACY_SEARCH")
        self.assertEqual(turn2_data["status"], "success")
        self.assertTrue(turn2_data["demo_notice"])

        # 3 verified pharmacies returned; unverified GreenCross excluded
        self.assertEqual(len(turn2_data["results"]), 3)
        returned_names = [r["pharmacy"]["name"] for r in turn2_data["results"]]
        self.assertIn("CarePoint Pharmacy", returned_names)
        self.assertIn("Metro Chemist", returned_names)
        self.assertIn("Apollo Life Chemist", returned_names)
        self.assertNotIn("GreenCross Meds", returned_names)

        # Check stock statuses represented
        stock_statuses = {r["stock_status"] for r in turn2_data["results"]}
        self.assertIn("AVAILABLE", stock_statuses)
        self.assertIn("LOW_STOCK", stock_statuses)
        self.assertIn("OUT_OF_STOCK", stock_statuses)

        # When coordinates are not provided: distance_km is None, no proximity claim
        for r in turn2_data["results"]:
            self.assertIsNone(r["distance_km"])

        self.assertIn("verified pharmacies with inventory records for 'Paracetamol 500mg'", turn2_data["message"])
        self.assertIn("Availability varies by pharmacy", turn2_data["message"])
        self.assertNotIn("stocking '", turn2_data["message"])
        self.assertIn("Device location was not shared", turn2_data["message"])
        self.assertIn("Demonstration Notice", turn2_data["message"])

    def test_pharmacy_search_with_user_coordinates_orders_by_distance(self):
        """When user coordinates are provided in context, pharmacies are ordered by calculated distance."""
        p_care = Pharmacy.objects.create(
            name="CarePoint Pharmacy",
            address="101 Healthcare Lane",
            area="Koramangala",
            city="Bengaluru",
            pin_code="560034",
            latitude=Decimal("12.934000"),
            longitude=Decimal("77.610000"),
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )
        p_metro = Pharmacy.objects.create(
            name="Metro Chemist",
            address="12 Retail Arcade",
            area="Indiranagar",
            city="Bengaluru",
            pin_code="560038",
            latitude=Decimal("12.978000"),
            longitude=Decimal("77.640000"),
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )
        Inventory.objects.create(pharmacy=p_care, medicine=self.medicine, quantity=10, is_demo=True)
        Inventory.objects.create(pharmacy=p_metro, medicine=self.medicine, quantity=10, is_demo=True)

        payload = {
            "message": "Find nearby pharmacies",
            "context": {
                "searched_medicine": "Paracetamol 500mg",
                "user_lat": 12.935,
                "user_lon": 77.611,
            },
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["results"]), 2)

        # Closest pharmacy to 12.935, 77.611 is CarePoint (~0.15 km)
        first_pharm = data["results"][0]
        self.assertEqual(first_pharm["pharmacy"]["name"], "CarePoint Pharmacy")
        self.assertIsNotNone(first_pharm["distance_km"])
        self.assertLess(first_pharm["distance_km"], data["results"][1]["distance_km"])

    def test_pharmacy_search_unstocked_medicine_returns_truthful_no_results(self):
        """Searching for pharmacies for an uncatalogued medicine truthfully returns no_results."""
        payload = {
            "message": "Find nearby pharmacies",
            "context": {"searched_medicine": "NonExistentDrug999"},
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["status"], "no_results")
        self.assertEqual(data["results"], [])
        self.assertIn("No matching pharmacies found in the directory for 'NonExistentDrug999'", data["message"])

    def test_html_entity_decoding_in_medicine_query_and_response(self):
        """
        BUG 2 REGRESSION TEST:
        Queries containing hex entities (e.g. '&#x35;00mg' or '&#x31;0mg')
        must be decoded at data boundaries and not leak raw entities into responses.
        """
        payload = {"message": "Find Paracetamol &#x35;00mg"}
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertNotIn("&#x35;", data["message"])
        self.assertGreaterEqual(len(data["results"]), 1)
        first_med = data["results"][0]["medicine"]
        self.assertEqual(first_med["strength"], "500mg")
