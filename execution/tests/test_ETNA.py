from unittest.mock import Mock
from django.test import TestCase
from execution.ETNA_api.send_orders import _login, get_accounts_ETNA, _get_current_account_id, get_current_login, \
    _get_security_ETNA, get_security, send_order_ETNA, logout, update_ETNA_order_status, insert_order_ETNA
from execution.models import OrderETNA, ETNALogin
from execution.ETNA_api.send_orders import ResponseCode
from local_settings import ETNA_ACCOUNT_ID
# demo.etnatrader.com

# connect ETNA models to ORDER models


class BaseTest(TestCase):
    def setUp(self):
        self.login = get_current_login()

    def test_ETNA_login(self):
        login_response = get_current_login()
        self.assertTrue(len(login_response.Ticket) == 520)
        self.assertTrue(login_response.ResponseCode == 0)
        self.assertTrue(len(login_response.Result.SessionId) == 36)
        self.assertTrue(login_response.Result.UserId > 0)

    def test_ETNA_multiple_logins(self):
        _login()
        _login()
        get_current_login()
        logins = ETNALogin.objects.filter(ResponseCode=ResponseCode.Valid.value)
        self.assertTrue(len(logins) == 1)

    def test_get_accounts(self):
        get_accounts_ETNA(self.login.Ticket)
        account_number = _get_current_account_id()
        self.assertTrue(account_number > 0)

    def test_get_security(self):
        etna_security = get_security('GOOG')
        self.assertTrue(etna_security.Symbol == 'GOOG')
        self.assertTrue(etna_security.symbol_id == 5)

    def test_send_trade(self):
        symbol = 'GOOG'
        etna_order = insert_order_ETNA(10, 1, OrderETNA.SideChoice.Buy.value, symbol)
        order = send_order_ETNA(etna_order, self.login.Ticket, ETNA_ACCOUNT_ID)
        self.assertTrue(order.Order_Id != -1)
        return order

    def test_update_order_status(self):
        order = self.test_send_trade()
        nothing = OrderETNA.objects.is_complete()
        something = OrderETNA.objects.is_not_complete()

        self.assertTrue(len(nothing) == 0)
        self.assertTrue(len(something) == 1)
        self.assertTrue(order.is_complete is False)

        order = update_ETNA_order_status(order.Order_Id, self.login.Ticket)
        one_order = OrderETNA.objects.is_complete()
        nothing = OrderETNA.objects.is_not_complete()
        self.assertTrue(len(one_order) == 1)
        self.assertTrue(len(nothing) == 0)
        self.assertTrue(order.is_complete is True)
        self.assertTrue(order.Status == OrderETNA.StatusChoice.Rejected.value)

    def tearDown(self):
        logout(self.login.Ticket)
