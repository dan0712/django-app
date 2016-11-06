from unittest.mock import Mock
from django.test import TestCase
from execution.ETNA_api.send_orders import login, get_accounts_ETNA, get_current_account_id, get_current_login, \
    get_security_ETNA, get_security, send_order_ETNA, logout, set_logged_out
from execution.models import OrderETNA


class BaseTest(TestCase):
    def setUp(self):
        login()

    def test_ETNA_login(self):
        login_response = get_current_login()
        self.assertTrue(len(login_response.Ticket) == 520)
        self.assertTrue(login_response.ResponseCode == 0)
        self.assertTrue(len(login_response.Result.SessionId) == 36)
        self.assertTrue(login_response.Result.UserId > 0)

    def test_get_accounts(self):
        get_accounts_ETNA()
        account_number = get_current_account_id()
        self.assertTrue(account_number > 0)

    def test_get_security(self):
        get_security_ETNA('GOOG')
        etna_security = get_security('GOOG')
        self.assertTrue(etna_security.Symbol == 'GOOG')
        self.assertTrue(etna_security.symbol_id == 5)

    def test_send_trade(self):
        get_accounts_ETNA()
        params = {'Price': 10,
                  'Quantity': 1,
                  'SecurityId': 5,
                  'Side': 0,
                  'TimeInForce': 0,
                  'ExpireDate': 0}

        order = OrderETNA.objects.get_or_create(id=1, defaults=params)[0]
        send_order_ETNA(order)
        self.assertTrue(True)

    def tearDown(self):
        logout()
