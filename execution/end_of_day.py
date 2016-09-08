import logging
from django.db import transaction
from functools import partial
from logging import DEBUG, INFO, WARN, ERROR
from time import sleep, strftime, time
from execution.broker.interactive_brokers import InteractiveBrokers
from execution.account_groups.create_account_groups import FAAccountProfile

from client.models import ClientAccount
from main.models import MarketOrderRequest, ExecutionRequest
from django.db.models import Q
from django.core.management.base import BaseCommand


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
    opts.verbose = 0
    return opts


def reconcile_cash_client_account(account):
    with transaction.atomic():
        account_cash = account.cash_balance
        goals = account.goals.all()

        goals_cash = 0
        for goal in goals:
            goals_cash += goal.cash_balance

        ib_account = account.ib_account
        ib_cash = ib_account_cash[ib_account.ib_account]

        difference = ib_cash - (account_cash + goals_cash)
        if difference > 0:
            #there was deposit
            account_cash += difference
        elif difference < 0:
            #withdrawals
            if abs(difference) < account_cash:
                account_cash -= abs(difference)
            else:
                logger.exception("interactive brokers cash < sum of goals cashes for " + ib_account.ib_account)
                raise Exception("interactive brokers cash < sum of goals cashes for " + ib_account.ib_account)
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


def get_execution_requests():
    client_accounts = ClientAccount.objects.all()
    ers = list()
    for account in client_accounts:
        mor_all = MarketOrderRequest.objects.all().filter(account=account)

        mor = list()
        for m in mor_all:
            if m.state == MarketOrderRequest.State.APPROVED.value or m.state == MarketOrderRequest.State.PENDING.value:
                mor.append(m)

        for m in mor:
            e = ExecutionRequest.objects.filter(order=m)
            ers.extend(e)
    return ers


def transform_execution_requests(execution_requests):
    shares = set()
    for e in execution_requests:
        shares.add(e.asset.symbol)

    allocations = dict()
    for s in shares:
        allocations[s] = dict()
        for e in execution_requests:
            if e.asset.symbol == s:
                mor = MarketOrderRequest.objects.get(execution_requests=e)
                ib_account = mor.account.ib_account.ib_account

                if ib_account not in allocations[s]:
                    allocations[s][ib_account] = e.volume
    return allocations


def main(options):
    logging.root.setLevel(verbose_levels.get(options.verbose, ERROR))
    con = InteractiveBrokers()
    con.connect()
    con.request_account_summary()

    con.request_market_depth('GOOG')
    while con.requesting_market_depth():
        short_sleep()

    long_sleep()
    long_sleep()
    long_sleep()

    account_dict = dict()
    account_dict['DU493341'] = 40
    account_dict['DU493342'] = 60
    profile = FAAccountProfile()
    profile.append_share_allocation('AAPL', account_dict)

    account_dict['DU493341'] = 60
    account_dict['DU493342'] = 40
    profile.append_share_allocation('MSFT', account_dict)
    con.replace_profile(profile.get_profile())

    #con.request_profile()
    short_sleep()

    order_id = con.make_order(ticker='MSFT', limit_price=57.57, quantity=100)
    con.place_order(order_id)

    order_id = con.make_order(ticker='AAPL', limit_price=107.59, quantity=-100)
    con.place_order(order_id)

    long_sleep()
    con.current_time()

    con.request_market_depth('GOOG')
    while con.requesting_market_depth():
        short_sleep()

    short_sleep()

    long_sleep()
    long_sleep()

    #reconcile_cash_client_accounts()


if __name__ == '__main__':
    #try:

        main(get_options())
    #except:
        print("exception")

'''
class Command(BaseCommand):
    help = 'execute orders'

    def handle(self, *args, **options):
        logger.setLevel(logging.DEBUG)
'''