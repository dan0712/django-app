import logging
from collections import defaultdict
from datetime import timedelta

import pandas as pd
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.db.models.query_utils import Q

from main.models import MarketOrderRequest, Transaction, Ticker, PositionLot
from .abstract import ExecutionProviderAbstract

logger = logging.getLogger('betasmartz.execution_provider_django')

class ExecutionProviderDjango(ExecutionProviderAbstract):

    def get_execution_request(self, reason):
        pass

    def create_market_order(self, account):
        order = MarketOrderRequest(account=account)
        return order

    def create_execution_request(self, reason, goal, asset, volume, order, limit_price):
        pass

    def get_asset_weights_without_tax_winners(self, goal):
        qs = Transaction.objects.filter(Q(to_goal=goal) | Q(from_goal=goal),
                                        reason=Transaction.REASON_EXECUTION).order_by('executed')

        txs = qs.values_list('execution_distribution__execution__executed',
                             'execution_distribution__execution__asset__id',
                             'execution_distribution__volume',
                             'execution_distribution__execution__price')
        executions_per_ticker = defaultdict(dict)
        prices_per_ticker = defaultdict(dict)
        for tx in txs:
            executions_per_ticker[tx[1]][tx[0]] = tx[2]
            prices_per_ticker[tx[1]][tx[0]] = tx[3]

        executions = self._construct_matrix(executions_per_ticker)
        executions = executions.sort_index(ascending=False)
        executions[executions < 0] = 0  # we take into account only buys/not sells

        prices = self._construct_matrix(prices_per_ticker)
        prices = prices.sort_index(ascending=False)
        prices[executions < 0] = 0  # we take into account only buys/not sells

        executions_cumsum = executions.cumsum()

        positions = goal.get_positions_all()

        weights = dict()
        bal = goal.available_balance
        for position in positions:
            if position.ticker.id not in executions:
                logger.warn("Position: {} has no matching executions.".format(position))
                continue

            date_of_first_lot = executions_cumsum[executions_cumsum[position.ticker.id] >= position.share].index[0]
            executions_single_asset = pd.DataFrame(executions[position.ticker.id][:date_of_first_lot])
            prices = pd.DataFrame(prices[position.ticker.id][:date_of_first_lot])

            # find lots with price > position.ticker.unit_price
            tax_winners_dates = prices[prices[position.ticker.id] > position.ticker.unit_price].index
            amount_of_tax_winners_per_ticker = int(executions_single_asset.ix[tax_winners_dates].sum())

            # search buys only
            if not executions_single_asset.empty:
                vol = min(amount_of_tax_winners_per_ticker, position.share)
                weights[position.ticker.id] = (vol * position.ticker.unit_price) / bal

        return weights

    def get_asset_weights_held_less_than1y(self, goal, today):
        m1y = today - timedelta(days=366)
        lots = PositionLot.objects.\
            filter(execution_distribution__execution__executed__gt=m1y,
                   execution_distribution__transaction__from_goal=goal).\
            annotate(tid=F('execution_distribution__execution__asset__id')).values('tid').\
            annotate(value=Coalesce(Sum(F('quantity') * F('execution_distribution__execution__asset__unit_price')), 0))

        weights = dict()

        bal = goal.available_balance
        for l in lots:
            weights[l['tid']] = l['value'] / bal
        return weights
