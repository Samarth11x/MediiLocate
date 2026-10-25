"""
Regression tests for URL routing and SPA fallback isolation.
Ensures:
- /admin/dashboard and /admin/dashboard/ route to React SPA admin portal.
- /admin/ and /admin/login/ route to Django Administration portal.
- /api/v1/* routes to REST API endpoints, never intercepted by SPA fallback.
- Client routes (/, /app, /login, /register, /pharmacist/dashboard) route to SPA.
"""

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status


class RoutingAndSpaFallbackTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_admin_dashboard_routes_to_spa(self):
        """GET /admin/dashboard must serve React SPA rather than 404 in Django Admin."""
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should set csrf cookie for SPA bootstrapping
        self.assertIn('csrftoken', response.cookies)

    def test_admin_dashboard_trailing_slash_routes_to_spa(self):
        """GET /admin/dashboard/ must serve React SPA."""
        response = self.client.get('/admin/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrftoken', response.cookies)

    def test_django_admin_root_preserved(self):
        """GET /admin/ must serve Django Administration portal (200 or 302 to login)."""
        response = self.client.get('/admin/', follow=False)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_302_FOUND])
        if response.status_code == status.HTTP_302_FOUND:
            self.assertTrue(response.url.startswith('/admin/login'))

    def test_django_admin_login_preserved(self):
        """GET /admin/login/ must serve Django Admin login form."""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Django administration')

    def test_client_portal_routes_serve_spa(self):
        """Client frontend routes must resolve to SPA."""
        routes = ['/', '/app', '/login', '/register', '/pharmacist/dashboard']
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn('csrftoken', response.cookies)

    def test_api_endpoints_not_intercepted_by_spa(self):
        """API endpoints under /api/v1/ must return API responses, not HTML."""
        # Health check
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get('Content-Type'), 'application/json')
        self.assertEqual(response.json()['status'], 'ok')

        # Auth Me (unauthenticated session check)
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get('Content-Type'), 'application/json')
        self.assertFalse(response.json()['authenticated'])

        # Protected Pharmacist endpoint (unauthenticated)
        response = self.client.get('/api/v1/pharmacist/inventory/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        self.assertEqual(response.headers.get('Content-Type'), 'application/json')
