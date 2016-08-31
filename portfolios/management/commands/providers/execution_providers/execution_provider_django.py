from portfolios.management.commands.providers.execution_providers.execution_provider_abstract \
    import ExecutionProviderAbstract
from django.db.models.query_utils import Q
from main.models import ExecutionRequest, MarketOrderRequest, Execution, Transaction
import pandas as pd
from datetime import timedelta


class ExecutionProviderDjango(ExecutionProviderAbstract):

    def get_execution_request(self, reason):
        ExecutionRequest.reason = ExecutionRequest.Reason(reason)
        return ExecutionRequest

    def create_market_order(self, account):
        order = MarketOrderRequest(account=account)
        return order

    def create_execution_request(self, reason, goal, asset, volume, order, limit_price):
        pass

    def get_asset_weights_held_less_than1y(self, goal, today):
        assets_held_less = dict()

        qs = Transaction.objects.filter(Q(to_goal=goal) | Q(from_goal=goal),
                                        reason=Transaction.REASON_EXECUTION).order_by('executed')

        txs = qs.values_list('execution_distribution__execution__executed',
                             'execution_distribution__execution__asset__id',
                             'execution_distribution__volume')

        executions = self._construct_matrix('volume', txs)
        executions = executions.sort_index(ascending=False)
        executions[executions < 0] = 0 #we take into account only buys/not sells
        executions = executions.cumsum()

        positions = goal.get_positions_all()

        for position in positions:
            # search this year's buys only
            executions_single_asset = pd.DataFrame(executions[position.ticker.symbol])
            executions_this_year = executions_single_asset[today-timedelta(365):]
            assets_held_less[position.ticker.symbol] = min(int(executions_this_year.iloc[-1]), position.share)

        weights = dict()
        for pos in positions:
            value = (assets_held_less[pos.ticker.id] * pos.ticker.daily_prices.last()) / goal.available_balance
            weights[pos.ticker.id] = value
        return weights


