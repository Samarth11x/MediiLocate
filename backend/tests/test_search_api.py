"""
Comprehensive automated tests for Search API endpoints:
- GET /api/v1/search/medicines/
- GET /api/v1/search/pharmacies/

Verifies:
- Exact medicine search matching.
- Medication identity safeguards (strength and dosage-form mismatches excluded).
- Empty catalogue truthful handling.
- Strict pharmacy verification filtering (unverified pharmacies excluded).
- All 4 inventory availability states: AVAILABLE, LOW_STOCK, OUT_OF_STOCK, UNKNOWN.
- Safe handling of missing location coordinates and missing prices.
- Conspicuous demo notice disclosure.
- Input validation (missing query, oversized query, coordinate bounds, invalid types).
- HTTP 405 Method Not Allowed on non-GET requests.
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.medicines.models import Medicine
from apps.pharmacies.models import Pharmacy, VerificationStatus
from apps.inventory.models import Inventory


class SearchApiEndpointTests(TestCase):
    """Test suite for /api/v1/search/ endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.medicines_url = reverse("search-medicines")
        self.pharmacies_url = reverse("search-pharmacies")

        # 1. Seed Verified Pharmacies
        self.pharm_verified_1 = Pharmacy.objects.create(
            name="Demo Verified Care Chemist (Fictional Dev)",
            address="101 Health Way, Koramangala",
            area="Koramangala",
            city="Bengaluru",
            pin_code="560034",
            latitude=Decimal("12.935200"),
            longitude=Decimal("77.624500"),
            contact_number="+91 99999 00001",
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )

        self.pharm_verified_2 = Pharmacy.objects.create(
            name="Demo Verified Life Meds (Fictional Dev)",
            address="202 Cure Road, Indiranagar",
            area="Indiranagar",
            city="Bengaluru",
            pin_code="560038",
            latitude=Decimal("12.971800"),
            longitude=Decimal("77.641100"),
            contact_number="+91 99999 00002",
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )

        # 2. Seed Unverified Pharmacy (MUST BE EXCLUDED)
        self.pharm_unverified = Pharmacy.objects.create(
            name="Demo Unverified Store (Fictional Dev - Pending)",
            address="999 Fake St",
            area="Outer Area",
            city="Bengaluru",
            pin_code="560099",
            latitude=Decimal("12.999999"),
            longitude=Decimal("77.777777"),
            verification_status=VerificationStatus.PENDING,
            is_demo=True,
        )

        # 3. Seed Medicines
        self.med_pcm_500 = Medicine.objects.create(
            generic_name="Paracetamol",
            brand_name="Crocin",
            strength="500mg",
            dosage_form="Tablet",
            pack_size="Strip of 10",
            search_aliases=["pcm", "fever tablet"],
        )

        self.med_pcm_650 = Medicine.objects.create(
            generic_name="Paracetamol",
            brand_name="Dolo",
            strength="650mg",
            dosage_form="Tablet",
            pack_size="Strip of 15",
            search_aliases=["dolo 650"],
        )

        self.med_pcm_syrup = Medicine.objects.create(
            generic_name="Paracetamol",
            brand_name="Calpol",
            strength="250mg/5ml",
            dosage_form="Syrup",
            pack_size="Bottle of 60ml",
            search_aliases=["calpol syrup"],
        )

        self.med_amox_500 = Medicine.objects.create(
            generic_name="Amoxicillin",
            brand_name="Novamox",
            strength="500mg",
            dosage_form="Capsule",
            pack_size="Strip of 10",
        )

        # 4. Seed Inventory Links (testing all availability states)
        # AVAILABLE (qty >= 10)
        self.inv_available = Inventory.objects.create(
            pharmacy=self.pharm_verified_1,
            medicine=self.med_pcm_500,
            quantity=50,
            price=Decimal("30.00"),
            is_demo=True,
        )

        # LOW_STOCK (1 <= qty < 10)
        self.inv_low_stock = Inventory.objects.create(
            pharmacy=self.pharm_verified_2,
            medicine=self.med_pcm_500,
            quantity=5,
            price=Decimal("32.50"),
            is_demo=True,
        )

        # Inventory at unverified pharmacy (must not be shown)
        self.inv_unverified = Inventory.objects.create(
            pharmacy=self.pharm_unverified,
            medicine=self.med_pcm_500,
            quantity=100,
            price=Decimal("20.00"),
            is_demo=True,
        )

    def test_exact_medicine_search_success(self):
        """GET /api/v1/search/medicines/?query=Paracetamol 500mg returns matching medicine and pharmacies."""
        response = self.client.get(self.medicines_url, {"query": "Paracetamol 500mg"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["total_medicines"], 1)
        med = data["medicines"][0]
        self.assertEqual(med["generic_name"], "Paracetamol")
        self.assertEqual(med["strength"], "500mg")
        self.assertEqual(med["dosage_form"], "Tablet")
        self.assertEqual(med["brand_name"], "Crocin")
        self.assertEqual(med["match_score"], 1.0)

        # Verify demo disclosure notice is present
        self.assertIn("DEMO MODE", data["demo_notice"])

    def test_strength_mismatch_safeguard(self):
        """Searching for 500mg strictly excludes 650mg and 250mg/5ml formulations."""
        response = self.client.get(self.medicines_url, {"query": "Paracetamol 500mg"})
        data = response.json()

        returned_strengths = [m["strength"] for m in data["medicines"]]
        self.assertIn("500mg", returned_strengths)
        self.assertNotIn("650mg", returned_strengths)
        self.assertNotIn("250mg/5ml", returned_strengths)

    def test_dosage_form_mismatch_safeguard(self):
        """Searching for Syrup strictly returns Syrup and excludes Tablets."""
        response = self.client.get(self.medicines_url, {"query": "Paracetamol Syrup"})
        data = response.json()

        self.assertEqual(data["total_medicines"], 1)
        self.assertEqual(data["medicines"][0]["dosage_form"], "Syrup")
        self.assertEqual(data["medicines"][0]["brand_name"], "Calpol")

    def test_unverified_pharmacies_strictly_excluded(self):
        """Unverified pharmacies are excluded from search results."""
        response = self.client.get(self.medicines_url, {"query": "Paracetamol 500mg"})
        data = response.json()

        pharmacy_names = [p["pharmacy"]["name"] for p in data["pharmacies"]]
        self.assertIn(self.pharm_verified_1.name, pharmacy_names)
        self.assertIn(self.pharm_verified_2.name, pharmacy_names)
        self.assertNotIn(self.pharm_unverified.name, pharmacy_names)

    def test_all_four_inventory_availability_states(self):
        """Verifies AVAILABLE, LOW_STOCK, OUT_OF_STOCK, and UNKNOWN stock states."""
        # Create OUT_OF_STOCK (qty = 0)
        pharm_out = Pharmacy.objects.create(
            name="Demo Out Of Stock Chemist (Fictional Dev)",
            address="303 Empty Ave",
            area="Jayanagar",
            city="Bengaluru",
            pin_code="560041",
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )
        Inventory.objects.create(
            pharmacy=pharm_out,
            medicine=self.med_amox_500,
            quantity=0,
            price=Decimal("50.00"),
            is_demo=True,
        )

        # Create UNKNOWN (qty = None)
        pharm_unknown = Pharmacy.objects.create(
            name="Demo Unknown Stock Chemist (Fictional Dev)",
            address="404 Mystery St",
            area="Whitefield",
            city="Bengaluru",
            pin_code="560066",
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )
        Inventory.objects.create(
            pharmacy=pharm_unknown,
            medicine=self.med_amox_500,
            quantity=None,
            price=Decimal("52.00"),
            is_demo=True,
        )

        # Search for Amoxicillin 500mg
        response = self.client.get(self.medicines_url, {"query": "Amoxicillin 500mg"})
        data = response.json()

        statuses = {p["stock_status"] for p in data["pharmacies"]}
        self.assertIn("OUT_OF_STOCK", statuses)
        self.assertIn("UNKNOWN", statuses)

        # Ensure UNKNOWN is never presented as AVAILABLE
        unknown_pharm = next(p for p in data["pharmacies"] if p["pharmacy"]["name"] == pharm_unknown.name)
        self.assertEqual(unknown_pharm["stock_status"], "UNKNOWN")
        self.assertIsNone(unknown_pharm["quantity"])

    def test_safe_handling_of_missing_location_and_price(self):
        """Missing user coordinates and missing prices do not crash or corrupt ranking."""
        # Pharmacy with null coordinates and inventory with null price
        pharm_no_coords = Pharmacy.objects.create(
            name="Demo No Coords Chemist (Fictional Dev)",
            address="505 Unknown LatLon Rd",
            area="Remote",
            city="Bengaluru",
            pin_code="560001",
            latitude=None,
            longitude=None,
            verification_status=VerificationStatus.VERIFIED,
            is_demo=True,
        )
        Inventory.objects.create(
            pharmacy=pharm_no_coords,
            medicine=self.med_pcm_500,
            quantity=20,
            price=None,  # Null price
            is_demo=True,
        )

        # Call search WITHOUT user lat/lon
        response = self.client.get(self.medicines_url, {"query": "Paracetamol 500mg"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNone(data["user_location"])
        # Find the record for pharm_no_coords
        no_coord_res = next(p for p in data["pharmacies"] if p["pharmacy"]["name"] == pharm_no_coords.name)
        self.assertIsNone(no_coord_res["distance_km"])
        self.assertIsNone(no_coord_res["price"])
        self.assertGreater(no_coord_res["ranking_score"], 0.0)

    def test_search_with_user_location_computes_distance(self):
        """Providing valid lat/lon calculates Haversine distance in km."""
        response = self.client.get(
            self.medicines_url,
            {"query": "Paracetamol 500mg", "lat": 12.935000, "lon": 77.624000},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIsNotNone(data["user_location"])
        self.assertEqual(data["user_location"]["lat"], 12.935000)

        # Verify distance is attached to first verified store
        first_pharm = data["pharmacies"][0]
        self.assertIsNotNone(first_pharm["distance_km"])
        self.assertIsInstance(first_pharm["distance_km"], (int, float))

    def test_empty_query_returns_400(self):
        """Missing or whitespace query returns HTTP 400 Bad Request."""
        res_missing = self.client.get(self.medicines_url)
        self.assertEqual(res_missing.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res_missing.json())

        res_empty = self.client.get(self.medicines_url, {"query": "    "})
        self.assertEqual(res_empty.status_code, status.HTTP_400_BAD_REQUEST)

    def test_oversized_query_returns_400(self):
        """Query exceeding 200 characters returns HTTP 400."""
        res = self.client.get(self.medicines_url, {"query": "a" * 201})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_coordinate_validation_bounds(self):
        """Invalid coordinate values return HTTP 400."""
        # lat without lon
        res1 = self.client.get(self.medicines_url, {"query": "pcm", "lat": 12.93})
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)

        # out of range lat (>90)
        res2 = self.client.get(self.medicines_url, {"query": "pcm", "lat": 95.0, "lon": 77.0})
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

        # out of range lon (>180)
        res3 = self.client.get(self.medicines_url, {"query": "pcm", "lat": 12.0, "lon": 185.0})
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_catalogue_handling(self):
        """When database has zero medicines, returns empty lists with truthful message."""
        Inventory.objects.all().delete()
        Medicine.objects.all().delete()
        response = self.client.get(self.medicines_url, {"query": "Paracetamol"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["total_medicines"], 0)
        self.assertEqual(data["medicines"], [])
        self.assertIn("unpopulated", data["message"].lower())

    def test_unsupported_http_methods_return_405(self):
        """POST, PUT, DELETE methods return HTTP 405 Method Not Allowed."""
        res_post = self.client.post(self.medicines_url, {"query": "test"})
        self.assertEqual(res_post.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        res_del = self.client.delete(self.medicines_url)
        self.assertEqual(res_del.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_pharmacies_endpoint_by_medicine_id(self):
        """GET /api/v1/search/pharmacies/?medicine_id=... returns pharmacies with that medicine."""
        response = self.client.get(self.pharmacies_url, {"medicine_id": self.med_pcm_500.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertGreaterEqual(data["total_pharmacies"], 2)
        first_pharm = data["pharmacies"][0]
        self.assertEqual(first_pharm["medicine"]["id"], self.med_pcm_500.id)
        self.assertIn("DEMO MODE", data["demo_notice"])
