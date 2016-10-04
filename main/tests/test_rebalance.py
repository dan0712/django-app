from django import test

from main.tests.fixture import Fixture1
from api.v1.tests.factories import GoalFactory, PositionLotFactory, TickerFactory, \
    TransactionFactory, GoalSettingFactory, GoalMetricFactory, AssetFeatureValueFactory, GoalMetricGroupFactory
from main.models import Execution, ExecutionDistribution, MarketOrderRequest, \
    Transaction
from portfolios.providers.execution.django import ExecutionProviderDjango
from main.management.commands.rebalance import perturbate_mix

from main.models import Ticker, GoalMetric
from datetime import datetime, date


class RebalanceTest(test.TestCase):
    def test_perturbate_mix(self):
        t1 = TickerFactory.create(symbol='SPY', unit_price=5)
        t2 = TickerFactory.create(symbol='QQQ', unit_price=5)
        t3 = TickerFactory.create(symbol='TLT', unit_price=100)
        t4 = TickerFactory.create(symbol='IEF', unit_price=100)
        equity = AssetFeatureValueFactory.create(name='equity', assets=[t1, t2])
        bond = AssetFeatureValueFactory.create(name='bond', assets=[t3, t4])

        goal_settings = GoalSettingFactory.create()

        GoalMetricFactory.create(group=goal_settings.metric_group, feature=equity,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.05, configured_val=0.01)
        GoalMetricFactory.create(group=goal_settings.metric_group, feature=bond,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX, rebalance_thr=0.05, configured_val=0.01)

        goal = GoalFactory.create(active_settings=goal_settings, cash_balance=100)

        Fixture1.create_execution_details(goal, t1, 5, 4, date(2016, 1, 1))
        Fixture1.create_execution_details(goal, t2, 5, 4, date(2016, 1, 1))
        Fixture1.create_execution_details(goal, t3, 5, 90, date(2016, 1, 1))
        Fixture1.create_execution_details(goal, t4, 5, 90, date(2016, 1, 1))
        Fixture1.create_execution_details(goal, t4, 5, 90, date(2016, 1, 1))

        weights = perturbate_mix(goal, None)
        self.assertTrue(weights[t1.id] + weights[t2.id] < 0.01 + 0.05)
        self.assertTrue(weights[t3.id] + weights[t4.id] < 0.01 + 0.05)
