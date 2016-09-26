import logging
from functools import partial
from logging import DEBUG, INFO, WARN, ERROR
from time import sleep

from django.db import transaction
from client.models import ClientAccount, IBAccount
from execution.broker.interactive_brokers.interactive_brokers import InteractiveBrokers
from execution.broker.interactive_brokers.account_groups.create_account_groups import FAAccountProfile
from main.models import MarketOrderRequest, ExecutionRequest, Execution, Ticker, ApexOrder, MarketOrderRequestAPEX
import types
from collections import defaultdict
from django.db.models import Sum, F
from django.db.models.functions import Coalesce

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


def get_options():
    opts = types.SimpleNamespace()
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
    ers = ExecutionRequest.objects.all().filter(order__state=MarketOrderRequest.State.APPROVED.value)
    return ers


def transform_execution_requests(execution_requests):
    '''
    transform django ExecutionRequests into allocation object, which we will use to keep track of allocation fills
    :param execution_requests: list of ExecutionRequest
    :return:
    '''
    allocations = defaultdict(lambda: defaultdict(float))
    for e in execution_requests.select_related('order__account__ib_account__ib_account', 'asset__symbol'):
        allocations[e.asset.symbol][e.order.account.ib_account.ib_account] += e.volume
    return allocations

def create_apex_orders():
    '''
    from outstanding MOR and ER create MorApex and ApexOrder
    '''
    ers = ExecutionRequest.objects.all().filter(order__state=MarketOrderRequest.State.APPROVED.value)\
        .annotate(ticker_id=F('asset__id'))\
        .values('ticker_id')\
        .annotate(volume=Sum('volume'))

    for grouped_volume_per_share in ers:
        ticker = Ticker.objects.get(id=grouped_volume_per_share['ticker_id'])
        apex_order = ApexOrder.objects.create(ticker=ticker, volume=grouped_volume_per_share['volume'])

        mor_ids = MarketOrderRequest.objects.all().filter(state=MarketOrderRequest.State.APPROVED.value,
                                                          execution_requests__asset_id=ticker.id).\
            values_list('id', flat=True).distinct()

        for id in mor_ids:
            mor = MarketOrderRequest.objects.get(id=id)
            morApex, created = MarketOrderRequestAPEX.objects.get_or_create(market_order_request=mor,
                                                                            ticker=ticker,
                                                                            apex_order=apex_order)


def example_usage_with_IB():
    options = get_options()
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


'''
class Command(BaseCommand):
    help = 'execute orders'

    def handle(self, *args, **options):
        logger.setLevel(logging.DEBUG)
'''