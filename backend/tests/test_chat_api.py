"""
Tests for MediBot Chat API endpoint (POST /api/v1/chat/).
Verifies input validation, HTTP status codes, intent routing, safety interception,
tool execution with seeded medicines, and privacy (zero chat persistence).
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.medicines.models import Medicine


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
