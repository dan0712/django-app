from execution.broker.ibroker import IBroker
from ib.ext.ComboLeg import ComboLeg
from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter
from ib.ext.Order import Order as IBOrder

from ib.ext.ScannerSubscription import ScannerSubscription
from ib.ext.TickType import TickType
from ib.lib.logger import logger as basicConfig
from ib.opt import ibConnection, message
from time import sleep, strftime, time
from functools import partial
from execution.data_structures.market_depth import MarketDepth
from execution.order.order import Order
from datetime import datetime, timedelta

very_short_sleep = partial(sleep, 0.01)
short_sleep = partial(sleep, 1)
long_sleep = partial(sleep, 10)

class Object(object):
    pass


def get_options():
    opts = Object()
    opts.port = 7496
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

        self.connection.register(self._reply_next_valid_order_id, 'NextValidId')
        self.connection.register(self._update_account_value, 'AccountSummary')
        self.connection.register(self._reply_managed_accounts, 'ManagedAccounts')
        self.connection.register(self._reply_current_time, 'CurrentTime')
        self.connection.register(self._reply_realtime_snapshot,
                                 message.tickPrice,
                                 message.tickSize)

        self.connection.register(self._reply_place_order, 'OpenOrder', 'OrderStatus')
        self.connection.register(self._error_handler, 'Error')

        self.ib_account_cash = dict()
        self.ib_account_list = list()
        self.market_data = dict()

        self.orders = dict()
        self.filled_orders = dict()
        self.order_events = set()

        self._requested_tickers = dict()

        self._current_time = datetime.now()

        self._time_received_next_valid_order_id = None
        self._next_valid_order_id = None

    def _register(self, method, *subscription):
        self.connection.register(method, subscription)

    def _get_next_valid_order_id(self):
        """
        You must assign a unique order ID to each order you place. IB's servers
        keep track of the next available order ID you can use; this function
        requests that value from IB's servers, waits until IB sends a response,
        then returns the ID.
        """
        last_time = self._time_received_next_valid_order_id
        self.connection.reqIds(1)
        # Wait until IB sends the next valid ID
        while last_time == self._time_received_next_valid_order_id:
            very_short_sleep()
        return self._next_valid_order_id

    def _reply_next_valid_order_id(self, msg):
        self._next_valid_order_id = msg.orderId
        self._time_received_next_valid_order_id = datetime.now()

    def current_time(self):
        return self._current_time

    def request_current_time(self):
        self.connection.reqCurrentTime()

    def _reply_current_time(self, msg):
        self._current_time = datetime.fromtimestamp(msg.time)

    def connect(self):
        self.connection.connect()

    def disconnect(self):
        self.connection.eDisconnect()

    def place_orders(self):
        for ib_id, order in self.orders.items():
            self.place_order(ib_id)

    def place_order(self, ib_id):
        if ib_id not in self.orders or not self.orders[ib_id].new:
            return
        order = self.orders[ib_id]

        order.new = False
        self.connection.placeOrder(order.ib_id, order.contract, order.order)
        short_sleep()

    def make_order(self, ticker, quantity, limit_price):
        if quantity == 0 or limit_price <= 0:
            return

        ib_order = IBOrder()
        ib_order.m_lmtPrice = limit_price
        ib_order.m_orderType = 'LMT'
        ib_order.m_totalQuantity = quantity

        ib_order.m_tif = 'GTD'
        valid_till = self.current_time() + timedelta(minutes=5)
        ib_order.m_goodTillDate = valid_till.strftime('%Y%m%d %H:%M:%S')

        if quantity > 0:
            ib_order.m_action = 'BUY'
        else:
            ib_order.m_action = 'SELL'

        contract = make_contract(ticker)
        ib_id = self._get_next_valid_order_id()
        order = Order(order=ib_order, contract=contract, ib_id=ib_id)
        self.orders[order.ib_id] = order
        return order.ib_id

    def request_account_summary(self):
        reqId = self._get_next_valid_order_id()
        self.connection.reqAccountSummary(reqId, 'All', 'AccountType,TotalCashValue')
        short_sleep()
        self.connection.cancelAccountSummary(reqId)

    def request_market_depth(self, ticker):
        ticker_id = self._get_next_valid_order_id()
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

    def __create_fill_dict_entry(self, msg):
        self.filled_orders[msg.orderId] = msg

    def __create_fill(self, msg):
        self.filled_orders[msg.orderId] = msg

    def _error_handler(self, msg):
        print("Server Error: %s" % msg)

    def _reply_place_order(self, msg):

        #TODO ignore duplicate messages
        #https://www.interactivebrokers.com/en/software/api/apiguide/java/orderstatus.htm

        # TODO test this
        if msg.typeName == "openOrder" and \
                        msg.orderId not in self.filled_orders:
            self.__create_fill_dict_entry(msg)

        # Handle Fills
        if msg.typeName == "orderStatus" and msg.status == "Filled":
            self.create_fill(msg)
        print("Server Response: %s, %s\n" % (msg.typeName, msg))

    def _reply_managed_accounts(self, msg):
        print("%s, %s " % (msg.typeName, msg))
        accounts = msg.accountsList.split(',')
        self.ib_account_list = [a for a in accounts if a]

    def _reply_realtime_snapshot(self, msg):
        if msg.field not in range(0, 4):
            return

        ticker = self._requested_tickers[msg.tickerId]
        if ticker not in self.market_data:
            self.market_data[ticker] = MarketDepth()

        # https://www.interactivebrokers.com/en/software/api/apiguide/tables/tick_types.htm
        if msg.field == TickType.BID:
            print('%s: bid: %s' % (ticker, msg.price))
            self.market_data[ticker].levels[0].bid = msg.price
        elif msg.field == TickType.ASK:
            print('%s: ask: %s' % (ticker, msg.price))
            self.market_data[ticker].levels[0].ask = msg.price
        elif msg.field == TickType.BID_SIZE:
            print('%s: bidVolume: %s' % (ticker, msg.size))
            self.market_data[ticker].levels[0].bid_volume = msg.size
        elif msg.field == TickType.ASK_SIZE:
            print('%s: askVolume: %s' % (ticker, msg.size))
            self.market_data[ticker].levels[0].ask_volume = msg.size

        if self.market_data[ticker].levels[0].is_complete:
            self._requested_tickers.pop(msg.tickerId, None)

    def _reply_handler(self, msg):
        """Handles of server replies"""
        print("Server Response: %s, %s" % (msg.typeName, msg))







