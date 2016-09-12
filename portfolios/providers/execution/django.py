import logging
from collections import defaultdict
from datetime import timedelta

import pandas as pd
from django.db.models.query_utils import Q

from main.models import MarketOrderRequest, Transaction
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

    def get_asset_weights_held_less_than1y(self, goal, today):
        qs = Transaction.objects.filter(Q(to_goal=goal) | Q(from_goal=goal),
                                        reason=Transaction.REASON_EXECUTION).order_by('executed')

        txs = qs.values_list('execution_distribution__execution__executed',
                             'execution_distribution__execution__asset__id',
                             'execution_distribution__volume')
        executions_per_ticker = defaultdict(dict)
        for tx in txs:
            executions_per_ticker[tx[1]][tx[0]] = tx[2]

        executions = self._construct_matrix(executions_per_ticker)
        executions = executions.sort_index(ascending=False)
        executions[executions < 0] = 0  # we take into account only buys/not sells
        executions = executions.cumsum()

        positions = goal.get_positions_all()

        weights = dict()
        bal = goal.available_balance
        for position in positions:
            if position.ticker.id not in executions:
                logger.warn("Position: {} has no matching executions.".format(position))
                continue
            executions_single_asset = pd.DataFrame(executions[position.ticker.id])
            # search this year's buys only
            executions_this_year = executions_single_asset[today-timedelta(365):]
            if not executions_this_year.empty:
                vol = min(int(executions_this_year.iloc[-1]), position.share)
                weights[position.ticker.id] = (vol * position.ticker.unit_price) / bal

        return weights
