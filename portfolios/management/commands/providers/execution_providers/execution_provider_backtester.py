from portfolios.management.commands.providers.execution_providers.execution_provider_abstract \
    import ExecutionProviderAbstract, Reason
from portfolios.management.commands.providers.dummy_models.dummy_models \
    import ExecutionRequestMock, MarketOrderRequestMock, ExecutionMock

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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
        assets_held_less = dict()

        executions = self._construct_matrix('volume',self.executions)
        executions = executions.sort_index(ascending=False)
        executions[executions < 0] = 0 #we take into account only buys/not sells
        executions = executions.cumsum()

        positions = goal.get_positions_all()

        for position in positions:
            # search this year's buys only
            executions_single_asset = pd.DataFrame(executions[position.ticker.symbol])
            executions_this_year = executions_single_asset[executions_single_asset.index > today-timedelta(365)]
            assets_held_less[position.ticker.symbol] = min(int(executions_this_year.iloc[-1]), position.share)

        weights = dict()
        for pos in positions:
            value = (assets_held_less[pos.ticker.id] * pos.ticker.daily_prices.last()) / goal.available_balance
            weights[pos.ticker.id] = value
        return weights

    def cash_left(self, time, cash):
        self.cash[time] = float(cash)

    def calculate_portfolio_returns(self):
        cash = pd.DataFrame.from_dict(self.cash, orient='index')
        cash.index = pd.to_datetime(cash.index)
        cash = cash.sort_index()
        cash.columns = ['cash']

        executions = self._construct_matrix('volume', self.executions)
        prices = self._construct_matrix('price', self.executions)
        allocations = executions.cumsum()

        shares_value = pd.DataFrame(np.sum(allocations * prices, 1), columns=['shares_value'])
        portfolio_value = pd.concat([shares_value, cash], axis=1)
        returns = np.sum(portfolio_value, 1).pct_change(1)
        return returns

    def attribute_sell(self, execution_request, goal):
        if execution_request.volume > 0:
            return

        executions = self._construct_matrix('volume', self.executions)
        executions = executions[execution_request.asset.id]
        executions = executions.sort_index(ascending=False)
        executions[executions < 0] = 0 #we take into account only buys/not sells
        executions = executions.cumsum()

        positions = goal.get_positions_all()
        shares_held_after_sell = sum([p.share if p.ticker == execution_request.asset.id else 0 for p in positions])
        shares_held_before_sell = shares_held_after_sell + abs(execution_request.volume)

        executions_before_sell_date = executions[executions >= shares_held_before_sell].index[0]
        executions_after_sell_date = executions[executions >= shares_held_after_sell].index[0]

        lot_dates = executions.index[executions_before_sell_date:executions_after_sell_date].index

        affected_lots = {}
        total_sell_volume = abs(execution_request.volume)
        for execution in reversed(self.executions):
            if execution.executed in lot_dates and \
                            execution.asset.id == execution_request.asset.id and \
                            execution.volume < 0:
                info = dict()
                info['price'] = execution.price

                if total_sell_volume > execution.volume:
                    total_sell_volume -= execution.volume
                    info['volume'] = execution.volume
                else:
                    info['volume'] = int(total_sell_volume)
                    total_sell_volume = 0
                affected_lots[execution.executed] = info

        below_1y_amount = 0
        above_1y_amount = 0
        below_1y_volume = 0
        above_1y_volume = 0
        for date, lot in affected_lots.items():
            if execution_request.executed - timedelta(days=365) > date:
                above_1y_amount += lot['volume']*lot['price']
                above_1y_volume += lot['volume']
            else:
                below_1y_amount += lot['volume']*lot['price']
                below_1y_volume += lot['volume']

        last_sell = self.executions[-1]
        below_1y_amount -= last_sell.price * below_1y_volume
        above_1y_amount -= last_sell.price * above_1y_volume

        if below_1y_amount > 0:
            self.gains_losses['below_1y_gains'] += below_1y_amount
        else:
            self.gains_losses['below_1y_losses'] += below_1y_amount

        if above_1y_amount > 0:
            self.gains_losses['above_1y_gains'] += above_1y_amount
        else:
            self.gains_losses['above_1y_losses'] += above_1y_amount

