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
