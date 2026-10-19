from django.test import TestCase

class AccountsAppTests(TestCase):
    def test_app_configured(self):
        from django.apps import apps
        app_config = apps.get_app_config('accounts')
        self.assertEqual(app_config.name, 'apps.accounts')
