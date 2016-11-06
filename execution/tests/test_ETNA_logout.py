from execution.ETNA_api.send_orders import login, logout, set_logged_out, get_current_login
from django.test import TestCase


class BaseTest(TestCase):
    def setUp(self):
        login()

    def test_logout(self):
        logout()
        set_logged_out()

        with self.assertRaises(Exception) as context:
            get_current_login()
        self.assertTrue('we are currently not logged in' in str(context.exception))

