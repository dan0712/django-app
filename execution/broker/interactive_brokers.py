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
from execution.data_structures.market_depth import MarketDepth


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


def make_contract(symbol):
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = 'STK'
    contract.m_exchange = 'SMART'
    contract.m_primaryExch = 'SMART'
    contract.m_currency = 'USD'
    contract.m_localSymbol = symbol
    return contract


class InteractiveBrokers(IBroker):
    def __init__(self):
        options = get_options()
        basicConfig()
        self.connection = ibConnection(options.host, options.port, options.clientid)
        self.connection.register(self._update_account_value, 'AccountSummary')
        self.connection.register(self._reply_managed_accounts, 'ManagedAccounts')
        self.connection.register(self._reply_realtime_snapshot,
                                 message.tickPrice,
                                 message.tickSize)
        self.ib_account_cash = dict()
        self.ib_account_list = list()
        self.market_data = dict()
        self._requested_tickers = dict()

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

    def request_market_depth(self, ticker):
        ticker_id = gen_tick_id()
        contract = make_contract(ticker)
        self._requested_tickers[ticker_id] = contract.m_symbol
        self.connection.reqMktData(ticker_id, contract, '', True)
        short_sleep()
        self.connection.cancelMktData(ticker_id)

    def requesting_market_depth(self):
        if len(self._requested_tickers) > 0:
            return True
        else:
            return False

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

    def _reply_realtime_snapshot(self, msg):
        if msg.field not in range(0, 4):
            return

        ticker = self._requested_tickers[msg.tickerId]
        if ticker not in self.market_data:
            self.market_data[ticker] = MarketDepth()

        # https://www.interactivebrokers.com/en/software/api/apiguide/tables/tick_types.htm
        if msg.field == 1:
            print('%s: bid: %s' % (ticker, msg.price))
            self.market_data[ticker].levels[0].bid = msg.price
        elif msg.field == 2:
            print('%s: ask: %s' % (ticker, msg.price))
            self.market_data[ticker].levels[0].ask = msg.price
        elif msg.field == 0:
            print('%s: bidVolume: %s' % (ticker, msg.size))
            self.market_data[ticker].levels[0].bid_volume = msg.size
        elif msg.field == 3:
            print('%s: askVolume: %s' % (ticker, msg.size))
            self.market_data[ticker].levels[0].ask_volume = msg.size

        if self.market_data[ticker].levels[0].is_complete:
            self._requested_tickers.pop(msg.tickerId, None)

    def _reply_handler(self, msg):
        """Handles of server replies"""
        print("Server Response: %s, %s" % (msg.typeName, msg))







