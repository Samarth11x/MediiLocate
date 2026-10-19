from django.test import TestCase

class SearchAppTests(TestCase):
    def test_app_configured(self):
        from django.apps import apps
        app_config = apps.get_app_config('search')
        self.assertEqual(app_config.name, 'apps.search')
