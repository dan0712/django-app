from unittest.mock import Mock
from django.test import TestCase
from execution.ETNA_api.send_orders import _login, get_accounts_ETNA, get_current_account_id, get_current_login, \
    get_security_ETNA, get_security, send_order_ETNA, logout, update_ETNA_order_status
from execution.models import OrderETNA, ETNALogin
from execution.ETNA_api.send_orders import ResponseCode
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
        get_accounts_ETNA()
        account_number = get_current_account_id()
        self.assertTrue(account_number > 0)

    def test_get_security(self):
        get_security_ETNA('GOOG')
        etna_security = get_security('GOOG')
        self.assertTrue(etna_security.Symbol == 'GOOG')
        self.assertTrue(etna_security.symbol_id == 5)

    def test_send_trade(self):
        symbol = 'GOOG'
        get_security_ETNA(symbol)
        etna_security = get_security(symbol) # not sure if this gets us current price as well

        params = {'Price': etna_security.Price,
                  'Quantity': 1,
                  'SecurityId': etna_security.symbol_id,
                  'Side': 0,
                  'TimeInForce': 0,
                  'ExpireDate': 0}

        order = OrderETNA.objects.get_or_create(id=1, defaults=params)[0]
        get_accounts_ETNA()  # we need account for which we send order
        send_order_ETNA(order)
        self.assertTrue(order.Order_Id != -1)
        return order

    def test_update_order_status(self):
        order = self.test_send_trade()
        nothing = OrderETNA.objects.is_complete()
        something = OrderETNA.objects.is_not_complete()

        self.assertTrue(len(nothing) == 0)
        self.assertTrue(len(something) == 1)
        self.assertTrue(order.is_complete is False)

        order = update_ETNA_order_status(order.Order_Id)
        one_order = OrderETNA.objects.is_complete()
        nothing = OrderETNA.objects.is_not_complete()
        self.assertTrue(len(one_order) == 1)
        self.assertTrue(len(nothing) == 0)
        self.assertTrue(order.is_complete is True)
        self.assertTrue(order.Status == OrderETNA.StatusChoice.Rejected.value)

    def tearDown(self):
        logout(self.login.Ticket)
