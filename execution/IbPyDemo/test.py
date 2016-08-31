import logging
import sys

from functools import partial
from logging import DEBUG, INFO, WARN, ERROR
from optparse import OptionParser
from random import randint
from time import sleep, strftime, time

from ib.ext.ComboLeg import ComboLeg
from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter
from ib.ext.Order import Order
from ib.ext.ScannerSubscription import ScannerSubscription
from ib.lib.logger import logger as basicConfig
from ib.opt import ibConnection, message
from ib.opt import messagetools

error_msgs = {}
order_ids = [0]
tick_msgs = []
short_sleep = partial(sleep, 1)
long_sleep = partial(sleep, 10)
generic_tick_keys = '100,101,104,106,165,221,225,236'

verbose_levels = {
    3 : DEBUG,
    2 : INFO,
    1 : WARN,
    0 : ERROR,
    }

tickerIds = dict()

def next_order_id():
    return order_ids[-1]


def save_order_id(msg):
    order_ids.append(msg.orderId)


def save_tick(msg):
    tick_msgs.append(msg)


def get_options():
    version = '%prog 0.1'
    parser = OptionParser(version=version)
    add = parser.add_option
    add('-d', '--demo', dest='demo', action='store_true',
        help='Server using demo account, safe for placing orders')
    add('-m', '--messages', dest='printmsgs', action='store_true',
        help='Print message type names and exit')
    add('-s', '--show', dest='showmsgs', metavar='MSG[:MAX]', action='append',
        help=('Print no more than MAX messages of type MSG, may use ALL to '
              'print all messages, may be repeated'), default=[])
    add('-n', '--host', dest='host', default='localhost',
        help='Name or address of remote server (default: %default)')
    add('-p', '--port', dest='port', default=7496, type='int',
        help='Port number for remote connection (default: %default)')
    add('-c', '--client', dest='clientid', metavar='ID', default=0, type='int',
        help='Client id for remote connection (default: %default)')
    add('-v', '--verbose', default=0, action='count',
        help='Verbose output, may be repeated')
    opts, args = parser.parse_args()
    return opts


def error_handler(msg):
    """Handles the capturing of error messages"""
    print("Server Error: %s" % msg)


def reply_handler(msg):
    """Handles of server replies"""
    print("Server Response: %s, %s" % (msg.typeName, msg))
    pass



def my_BidAsk(msg):
    if msg.field == 1:
        print('%s: bid: %s' % (tickerIds[msg.tickerId]['symbol'], msg.price))
    elif msg.field == 2:
        print('%s: ask: %s' % (tickerIds[msg.tickerId]['symbol'], msg.price))
    elif msg.field == 0:
        print('%s: bidVolume: %s' % (tickerIds[msg.tickerId]['symbol'], msg.size))
    elif msg.field == 3:
        print('%s: askVolume: %s' % (tickerIds[msg.tickerId]['symbol'], msg.size))
    #https://www.interactivebrokers.com/en/software/api/apiguide/tables/tick_types.htm



def update_account_value(msg):
    """Handles of server replies"""
    if msg is not None and msg.tag == 'TotalCashValue':
        print("Account %s, cash: %s %s" % (msg.account, msg.value, msg.currency))


def gen_tick_id():
    i = randint(100, 10000)
    while True:
        yield i
        i += 1
if sys.version_info[0] < 3:
    gen_tick_id = gen_tick_id().next
else:
    gen_tick_id = gen_tick_id().__next__

7
def make_contract(symbol):
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = 'STK'
    contract.m_exchange = 'SMART'
    contract.m_primaryExch = 'SMART'
    contract.m_currency = 'USD'
    contract.m_localSymbol = symbol
    return contract


def request_market_depth(connection, options):
    ticker_id = gen_tick_id()
    contract = make_contract('GOOG')
    contract.m_exchange = 'BATS'
    connection.reqMktDepth(ticker_id, contract, 5)
    short_sleep()
    connection.cancelMktDepth(ticker_id)
    '''
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=0, operation=0, side=1, price=771.37, size=1>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=1, operation=0, side=1, price=770.92, size=2>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=2, operation=0, side=1, price=770.61, size=1>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=3, operation=0, side=1, price=770.22, size=1>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=4, operation=0, side=1, price=769.88, size=1>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=0, operation=0, side=0, price=771.91, size=1>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=1, operation=0, side=0, price=772.12, size=1>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=2, operation=0, side=0, price=772.36, size=1>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=3, operation=0, side=0, price=772.77, size=1>
Server Response: updateMktDepth, <updateMktDepth tickerId=5965, position=4, operation=0, side=0, price=772.8, size=1>
    '''



def request_market_data(connection, options, symbol):
    ticker_id = gen_tick_id()
    contract = make_contract(symbol)

    contract_dict = dict()
    contract_dict['symbol'] = contract.m_symbol
    tickerIds[ticker_id] = contract_dict

    connection.reqMktData(ticker_id, contract, '', True)
    short_sleep()
    connection.cancelMktData(ticker_id)


def request_account_summary(connection, options):
    reqId = gen_tick_id()
    connection.reqAccountSummary(reqId, 'All', 'AccountType,TotalCashValue')
    short_sleep()
    connection.cancelAccountSummary(reqId)


def test_000(connection, options):
    connection.setServerLogLevel(5)
    connection.reqCurrentTime()
    connection.reqAccountUpdates(1, '')
    connection.reqManagedAccts()
    connection.requestFA(connection.GROUPS)
    connection.replaceFA(connection.GROUPS, '')
    connection.reqIds(10)


def test_999(connection, options):
    short_sleep()
    connection.eDisconnect()


def main(options):
    basicConfig()
    logging.root.setLevel(verbose_levels.get(options.verbose, ERROR))
    options.port
    con = ibConnection(options.host, 7497, options.clientid)

    # con.registerAll(reply_handler)
    con.register(error_handler, 'Error')
    con.register(update_account_value, 'AccountSummary')
    con.register(my_BidAsk, message.tickPrice, message.tickSize)
    con.register(reply_handler, 'UpdateMktDepth')

    con.connect()
    short_sleep()

    request_account_summary(connection=con, options=options)
    request_market_data(connection=con, options=options, symbol='GOOG')
    request_market_data(connection=con, options=options, symbol='MSFT')
    request_market_depth(connection=con, options=options)

    #test_000(connection=con, options=options)
    #test_003(connection=con, options=options)
    #test_999(connection=con, options=options)

    sleep(2)
    con.eDisconnect()

if __name__ == '__main__':
    try:
        main(get_options())
    except (KeyboardInterrupt, ):
        print('\nKeyboard interrupt.\n')

