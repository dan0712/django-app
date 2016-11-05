from unittest.mock import Mock
from django.test import TestCase
from execution.ETNA_api.send_orders import login
from execution.models import ETNALogin


class BaseTest(TestCase):
    def test_ETNA_login(self):
        login()
        login_response = ETNALogin.objects.all().first()
        self.assertTrue(len(login_response.Ticket) == 520)
        self.assertTrue(login_response.ResponseCode == 0)
        self.assertTrue(len(login_response.Result.SessionId) == 36)
        self.assertTrue(login_response.Result.UserId > 0)

