from unittest.mock import Mock
from django.test import TestCase
from execution.ETNA_api.send_orders import login


class BaseTest(TestCase):
    def test_ETNA_login(self):
        login()
        self.assertTrue(True)
