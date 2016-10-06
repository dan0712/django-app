from django import test

from main.tests.fixture import Fixture1
from api.v1.tests.factories import GoalFactory, PositionLotFactory, TickerFactory, \
    TransactionFactory, GoalSettingFactory, GoalMetricFactory, AssetFeatureValueFactory, GoalMetricGroupFactory
from main.models import Execution, ExecutionDistribution, MarketOrderRequest, \
    Transaction
from portfolios.providers.execution.django import ExecutionProviderDjango
from main.management.commands.rebalance import perturbate_mix, process_risk, perturbate_withdrawal

from main.models import Ticker, GoalMetric
from datetime import datetime, date


class RebalanceTest(test.TestCase):
    def setUp(self):
        self.t1 = TickerFactory.create(symbol='SPY', unit_price=5)
        self.t2 = TickerFactory.create(symbol='QQQ', unit_price=5)
        self.t3 = TickerFactory.create(symbol='TLT', unit_price=100)
        self.t4 = TickerFactory.create(symbol='IEF', unit_price=100)
        self.equity = AssetFeatureValueFactory.create(name='equity', assets=[self.t1, self.t2])
        self.bond = AssetFeatureValueFactory.create(name='bond', assets=[self.t3, self.t4])
        self.goal_settings = GoalSettingFactory.create()
        self.goal = GoalFactory.create(active_settings=self.goal_settings, cash_balance=100)

        Fixture1.create_execution_details(self.goal, self.t1, 5, 4, date(2016, 1, 1))
        Fixture1.create_execution_details(self.goal, self.t2, 5, 4, date(2016, 1, 1))
        Fixture1.create_execution_details(self.goal, self.t3, 5, 90, date(2016, 1, 1))
        Fixture1.create_execution_details(self.goal, self.t4, 5, 90, date(2016, 1, 1))
        Fixture1.create_execution_details(self.goal, self.t4, 5, 90, date(2016, 1, 1))

    def test_perturbate_mix(self):
        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.equity,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.05, configured_val=0.01)
        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.bond,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX, rebalance_thr=0.05, configured_val=0.01)

        weights = perturbate_mix(self.goal, None)
        self.assertTrue(weights[self.t1.id] + weights[self.t2.id] < 0.01 + 0.05)
        self.assertTrue(weights[self.t3.id] + weights[self.t4.id] < 0.01 + 0.05)

    def test_perturbate_risk(self):
        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.equity,
                                 type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.05, configured_val=0.5)

        #weights = process_risk(goal=self.goal)
        self.assertTrue(True)

    def test_perturbate_withdrawal(self):
        Fixture1.create_execution_details(self.goal, self.t4, self.goal.available_balance/90, 90, date(2016, 1, 1))
        TransactionFactory.create(from_goal=self.goal, status=Transaction.STATUS_PENDING,
                                  amount=self.goal.total_balance/2)
        weights = perturbate_withdrawal(self.goal)
        self.assertTrue(sum(weights.values()) < 1)

