from collections import defaultdict
from datetime import timedelta

import numpy as np
import pandas as pd

from portfolios.providers.dummy_models import ExecutionMock, \
    ExecutionRequestMock, MarketOrderRequestMock, Sale
from .abstract import ExecutionProviderAbstract, Reason

TAXES_MORE1Y_HELD = 0.2
TAXES_LESS1Y_HELD = 0.3


class ExecutionProviderBacktester(ExecutionProviderAbstract):
    def __init__(self):
        self.market_order_request = None
        self.execution_requests = []
        self.executions = []
        self.cash = {}
        self.gains_losses = {'above_1y_gains':0, 'above_1y_losses':0, 'below_1y_gains':0, 'below_1y_losses':0}

    def get_execution_request(self, reason):
        ExecutionRequestMock.reason = Reason(reason)
        return ExecutionRequestMock

    def create_execution_request(self, reason, goal, asset, volume, order, limit_price):
        execution_request = ExecutionRequestMock(reason, goal, asset, volume, order)
        self.execution_requests.append(execution_request)

        if self.market_order_request is not None:
            self.market_order_request.execution_requests = self.execution_requests
        else:
            print("no market order request to append to")

        return execution_request

    def create_market_order(self, account):
        self.market_order_request = MarketOrderRequestMock(account=account)
        return self.market_order_request

    def cancel_pending_orders(self):
        self.market_order_request = None
        self.execution_requests = []

    def create_empty_market_order(self):
        self.create_market_order(account=None)
        self.market_order_request.execution_requests = []
        return self.market_order_request

    def order_executed(self, execution_request, price, time):
        execution = ExecutionMock(order=execution_request,
                                  volume=execution_request.volume,
                                  price=price,
                                  amount=execution_request.volume * price,
                                  executed=time,
                                  asset=execution_request.asset
                                  )
        self.executions.append(execution)

    def get_asset_weights_held_less_than1y(self, goal, today):
        m1y = today - timedelta(days=366)
        assets = defaultdict(float)

        for execution in self.executions:
            if execution.executed > m1y:
                assets[execution.asset.id] += execution.volume

        weights = dict()
        positions = goal.get_positions_all()

        for pos in positions:
            value = (assets[pos['ticker_id']] * float(pos['price'])) / goal.available_balance
            weights[pos['ticker_id']] = value
        return weights


    def cash_left(self, time, cash):
        self.cash[time] = float(cash)

    def calculate_portfolio_returns(self):
        cash = pd.DataFrame.from_dict(self.cash, orient='index')
        cash.index = pd.to_datetime(cash.index)
        cash = cash.sort_index()
        cash.columns = ['cash']

        ept = ExecutionProviderBacktester._build_executions_per_ticker('volume', self.executions)
        executions = self._construct_matrix(ept)
        ppt = ExecutionProviderBacktester._build_executions_per_ticker('price', self.executions)
        prices = self._construct_matrix(ppt)
        allocations = executions.cumsum()

        shares_value = pd.DataFrame(np.sum(allocations * prices, 1), columns=['shares_value'])
        portfolio_value = pd.concat([shares_value, cash], axis=1)
        returns = np.sum(portfolio_value, 1).pct_change(1)
        return returns

    @staticmethod
    def _build_executions_per_ticker(attribute, executions):
        executions_per_ticker = defaultdict(dict)
        for execution in executions:
            executions_per_ticker[execution.asset.id][execution.executed] = getattr(execution, attribute)
        return executions_per_ticker

    def attribute_sell(self, execution_request, goal, data_provider):
        #create sale and choose lot/s to decrease
        m1y = data_provider.get_current_date() - timedelta(days=366)
        if execution_request.volume > 0:
            return
        lots = goal.get_lots_symbol(execution_request.asset.id)
        unit_tax_costs = dict()

        id = 0
        for lot in lots:
            if lot['executed'] < m1y:
               lot['tax_bracket'] = TAXES_MORE1Y_HELD
            else:
                lot['tax_bracket'] = TAXES_LESS1Y_HELD
            ticker = data_provider.get_ticker(tid=lot['ticker_id'])
            lot['current_price'] = float(ticker.daily_prices.last())
            lot['unit_tax_cost'] = float((lot['current_price'] - lot['price']) * lot['tax_bracket'])
            lot['id'] = id
            unit_tax_costs[id] = lot['unit_tax_cost']
            id += 1

        s = sorted(unit_tax_costs.items(), key = lambda x:x[1], reverse=True)
        #left to do - start decreasing lots and creating sales
