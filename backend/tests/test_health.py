"""
Tests for MediLocate AI Health Check API endpoint.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

class HealthCheckEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api-health')

    def test_health_endpoint_success(self):
        """GET /api/v1/health/ returns HTTP 200 OK with exact specified payload."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_payload = {
            "status": "ok",
            "service": "MediLocate API",
        }
        self.assertEqual(response.json(), expected_payload)

    def test_health_endpoint_no_sensitive_data_exposed(self):
        """Health endpoint must not expose database credentials, hosts, or debug traces."""
        response = self.client.get(self.url)
        content_str = response.content.decode('utf-8')
        # Assert no sensitive keywords are leaked
        self.assertNotIn("password", content_str.lower())
        self.assertNotIn("secret", content_str.lower())
        self.assertNotIn("supabase", content_str.lower())
        self.assertNotIn("database", content_str.lower())
        self.assertNotIn("postgres", content_str.lower())
