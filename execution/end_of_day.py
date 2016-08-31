import logging
import sys
from django.db import transaction
from functools import partial
from logging import DEBUG, INFO, WARN, ERROR
from optparse import OptionParser
from random import randint
from time import sleep, strftime, time
from client.models import ClientAccount

from ib.ext.ComboLeg import ComboLeg
from ib.ext.Contract import Contract
from ib.ext.ExecutionFilter import ExecutionFilter
from ib.ext.Order import Order
from ib.ext.ScannerSubscription import ScannerSubscription
from ib.lib.logger import logger as basicConfig
from ib.opt import ibConnection, message
from ib.opt import messagetools

order_ids = [0]

short_sleep = partial(sleep, 1)
long_sleep = partial(sleep, 10)

verbose_levels = {
    3 : DEBUG,
    2 : INFO,
    1 : WARN,
    0 : ERROR,
    }


ib_account_list = list()
ib_account_cash = dict()

logger = logging.getLogger('betasmartz.daily_process')
logger.setLevel(logging.INFO)


class Object(object):
    pass


def get_options():
    opts = Object()
    opts.port = 7497
    opts.host = 'localhost'
    opts.clientid = 0
    opts.verbose = 0
    return opts


def next_order_id():
    return order_ids[-1]


def save_order_id(msg):
    order_ids.append(msg.orderId)


def update_account_value(msg):
    """Handles of server replies"""
    if msg is not None and msg.tag == 'TotalCashValue':
        print("Account %s, cash: %s %s" % (msg.account, msg.value, msg.currency))
        ib_account_cash[msg.account] = msg.value


def reconcile_cash_client_account(account):
    with transaction.atomic():
        account_cash = account.cash_balance
        goals = account.goals.all()

        goals_cash = 0
        for goal in goals:
            goals_cash += goal.cash_balance

        ib_cash = ib_account_cash[account.account_id]

        difference = ib_cash - (account_cash + goals_cash)
        if difference > 0:
            #there was deposit
            account_cash += difference
        elif difference < 0:
            #withdrawals
            if abs(difference) < account_cash:
                account_cash -= abs(difference)
            else:
                logger.exception("interactive brokers cash < sum of goals cashes for " + account.account_id)
                raise Exception
                # we have a problem - we should not be able to withdraw more than account_cash
        account.cash_balance = account_cash
        account.save()
        return difference


def reconcile_cash_client_accounts():
    client_accounts = ClientAccount.objects.all()
    with transaction.atomic():
        for account in client_accounts:
            try:
                reconcile_cash_client_account(account)
            except:
                print("exception")


def gen_tick_id():
    i = randint(100, 10000)
    while True:
        yield i
        i += 1
if sys.version_info[0] < 3:
    gen_tick_id = gen_tick_id().next
else:
    gen_tick_id = gen_tick_id().__next__


def request_account_summary(connection, options):
    reqId = gen_tick_id()
    connection.reqAccountSummary(reqId, 'All', 'AccountType,TotalCashValue')
    short_sleep()
    connection.cancelAccountSummary(reqId)


def reply_handler(msg):
    """Handles of server replies"""
    print("Server Response: %s, %s" % (msg.typeName, msg))
    pass


def reply_managed_accounts(msg):
    print("%s, %s " % (msg.typeName, msg))
    accounts = msg.accountsList.split(',')
    for account in accounts:
        ib_account_list.append(account)


def main(options):
    basicConfig()
    logging.root.setLevel(verbose_levels.get(options.verbose, ERROR))
    con = ibConnection(options.host, options.port, options.clientid)
    con.register(update_account_value, 'AccountSummary')
    con.register(reply_managed_accounts, 'ManagedAccounts')
    con.connect()
    short_sleep()
    request_account_summary(connection=con, options=options)
    long_sleep()
    reconcile_cash_client_accounts()


if __name__ == '__main__':
    try:
        main(get_options())
    except:
        print("exception")