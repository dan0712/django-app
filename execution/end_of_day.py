import logging
from functools import partial
from logging import DEBUG, INFO, WARN, ERROR
from time import sleep

from django.db import transaction
from client.models import ClientAccount, IBAccount
from execution.broker.interactive_brokers.interactive_brokers import InteractiveBrokers
from execution.broker.interactive_brokers.account_groups.create_account_groups import FAAccountProfile
from main.models import MarketOrderRequest, ExecutionRequest, Execution, Ticker, ApexOrder, MarketOrderRequestAPEX, \
    ApexFill, ExecutionApexFill, ExecutionDistribution, Transaction, PositionLot, Sale
import types
from collections import defaultdict
from django.db.models import Sum, F, Avg,Case, When, Value, FloatField
from django.db.models.functions import Coalesce
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from main.management.commands.rebalance import get_tax_lots
from main.management.commands.rebalance import TAX_BRACKET_LESS1Y, TAX_BRACKET_MORE1Y

short_sleep = partial(sleep, 1)
long_sleep = partial(sleep, 10)

tax_bracket_egt1Y = 0.2
tax_bracket_lt1Y = 0.3

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


@transaction.atomic()
def reconcile_cash_client_account(account):
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
    sent_mor_ids = set()
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
            sent_mor_ids.add(id)
            mor = MarketOrderRequest.objects.get(id=id)
            MarketOrderRequestAPEX.objects.create(market_order_request=mor, ticker=ticker, apex_order=apex_order)

    for sent_id in sent_mor_ids:
        mor = MarketOrderRequest.objects.get(id=sent_id)
        mor.state = MarketOrderRequest.State.SENT.value
        mor.save()


def send_apex_order(apex_order):
    apex_order.state = ApexOrder.State.SENT.value
    apex_order.save()


@transaction.atomic
def process_apex_fills():
    '''
    from existing apex fills create executions, execution distributions, transactions and positionLots - pro rata all fills
    :return:
    '''
    fills = ApexFill.objects\
        .filter(apex_order__state=ApexOrder.State.SENT.value)\
        .annotate(ticker_id=F('apex_order__ticker__id'))\
        .values('id', 'ticker_id', 'price', 'volume','executed')

    complete_mor_ids = set()
    complete_apex_order_ids = set()
    for fill in fills:
        ers = ExecutionRequest.objects\
            .filter(asset_id=fill['ticker_id'], order__morsAPEX__apex_order__state=ApexOrder.State.SENT.value)
        sum_ers = np.sum([er.volume for er in ers])

        for er in ers:
            pro_rata = er.volume/float(sum_ers)
            volume = fill['volume'] * pro_rata

            apex_fill = ApexFill.objects.get(id=fill['id'])
            ticker = Ticker.objects.get(id=fill['ticker_id'])
            mor = MarketOrderRequest.objects.get(execution_requests__id=er.id)
            complete_mor_ids.add(mor.id)

            apex_order = ApexOrder.objects.get(morsAPEX__market_order_request__execution_requests__id=er.id)
            complete_apex_order_ids.add(apex_order.id)

            execution = Execution.objects.create(asset=ticker, volume=volume, price=fill['price'],
                                                 amount=volume*fill['price'], order=mor, executed=fill['executed'])
            ExecutionApexFill.objects.create(apex_fill=apex_fill, execution=execution)
            trans = Transaction.objects.create(reason=Transaction.REASON_ORDER,
                                               amount=volume*fill['price'],
                                               to_goal=er.goal, executed=fill['executed'])
            ed = ExecutionDistribution.objects.create(execution=execution, transaction=trans, volume=volume,
                                                      execution_request=er)

            if volume > 0:
                PositionLot.objects.create(quantity=volume, execution_distribution=ed)
            else:
                create_sale(ticker.id, volume, fill['price'], ed)

    for mor_id in complete_mor_ids:
        mor = MarketOrderRequest.objects.get(id=mor_id)
        mor.state = MarketOrderRequest.State.COMPLETE.value
        mor.save()

    for apex_order_id in complete_apex_order_ids:
        apex_order = ApexOrder.objects.get(id=apex_order_id)
        apex_order.state = ApexOrder.State.COMPLETE.value

        sum_fills = ApexFill.objects.filter(apex_order_id=apex_order_id).aggregate(sum=Sum('volume'))
        if sum_fills['sum'] == apex_order.volume:
            apex_order.fill_info = ApexOrder.FillInfo.FILLED.value
        elif sum_fills['sum'] == 0:
            apex_order.fill_info = ApexOrder.FillInfo.UNFILLED.value
        else:
            apex_order.fill_info = ApexOrder.FillInfo.PARTIALY_FILLED.value

        apex_order.save()


def create_sale(ticker_id, volume, current_price, execution_distribution):
    # start selling PositionLots from 1st until quantity sold == volume
    year_ago = timezone.now() - timedelta(days=366)
    position_lots = PositionLot.objects \
                    .filter(execution_distribution__execution__asset_id=ticker_id)\
                    .filter(quantity__gt=0)\
                    .annotate(price_entry=F('execution_distribution__execution__price'),
                              executed=F('execution_distribution__execution__executed'),
                              ticker_id=F('execution_distribution__execution__asset_id'))\
                    .annotate(tax_bracket=Case(
                      When(executed__gt=year_ago, then=Value(TAX_BRACKET_LESS1Y)),
                      When(executed__lte=year_ago, then=Value(TAX_BRACKET_MORE1Y)),
                      output_field=FloatField())) \
                    .annotate(unit_tax_cost=(current_price - F('price_entry')) * F('tax_bracket')) \
                    .order_by('unit_tax_cost')

    left_to_sell = abs(volume)
    for lot in position_lots:
        if left_to_sell == 0:
            break

        new_quantity = max(lot.quantity - left_to_sell, 0)
        left_to_sell -= lot.quantity - new_quantity
        lot.quantity = new_quantity
        lot.save()
        if new_quantity == 0:
            lot.delete()

        Sale.objects.create(quantity=- (lot.quantity - new_quantity),
                            sell_execution_distribution=execution_distribution,
                            buy_execution_distribution=lot.execution_distribution)


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