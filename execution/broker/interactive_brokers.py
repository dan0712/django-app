from execution.broker.ibroker import IBroker
from ib.ext.ComboLeg import ComboLeg
from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter
from ib.ext.Order import Order
from ib.ext.ScannerSubscription import ScannerSubscription
from ib.lib.logger import logger as basicConfig
from ib.opt import ibConnection, message
from time import sleep, strftime, time
from functools import partial
from random import randint
import sys


short_sleep = partial(sleep, 1)
long_sleep = partial(sleep, 10)


order_ids = [0]


def gen_tick_id():
    i = randint(100, 10000)
    while True:
        yield i
        i += 1
if sys.version_info[0] < 3:
    gen_tick_id = gen_tick_id().next
else:
    gen_tick_id = gen_tick_id().__next__


def next_order_id():
    return order_ids[-1]


def save_order_id(msg):
    order_ids.append(msg.orderId)


class Object(object):
    pass


def get_options():
    opts = Object()
    opts.port = 7497
    opts.host = 'localhost'
    opts.clientid = 0
    opts.verbose = 0
    return opts


class InteractiveBrokers(IBroker):
    def __init__(self):
        options = get_options()
        basicConfig()
        self.connection = ibConnection(options.host, options.port, options.clientid)
        self.connection.register(self._update_account_value, 'AccountSummary')
        self.connection.register(self._reply_managed_accounts, 'ManagedAccounts')
        self.ib_account_cash = dict()
        self.ib_account_list = list()

    def _register(self, method, *subscription):
        self.connection.register(method, subscription)

    def connect(self):
        self.connection.connect()

    def disconnect(self):
        self.connection.eDisconnect()

    def request_account_summary(self):
        reqId = gen_tick_id()
        self.connection.reqAccountSummary(reqId, 'All', 'AccountType,TotalCashValue')
        short_sleep()
        self.connection.cancelAccountSummary(reqId)

    def _update_account_value(self, msg):
        """Handles of server replies"""
        if msg is not None and msg.tag == 'TotalCashValue':
            print("Account %s, cash: %s %s" % (msg.account, msg.value, msg.currency))
            self.ib_account_cash[msg.account] = msg.value

    def _reply_managed_accounts(self, msg):
        print("%s, %s " % (msg.typeName, msg))
        accounts = msg.accountsList.split(',')
        for account in accounts:
            self.ib_account_list.append(account)

    def _reply_handler(self, msg):
        """Handles of server replies"""
        print("Server Response: %s, %s" % (msg.typeName, msg))







