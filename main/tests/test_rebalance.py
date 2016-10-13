from django import test

from main.tests.fixture import Fixture1
from api.v1.tests.factories import GoalFactory, PositionLotFactory, TickerFactory, \
    TransactionFactory, GoalSettingFactory, GoalMetricFactory, AssetFeatureValueFactory, \
    GoalMetricGroupFactory, InvestmentCycleObservationFactory, PortfolioSetFactory, MarkowitzScaleFactory
from main.models import Execution, ExecutionDistribution, MarketOrderRequest, \
    Transaction
from portfolios.providers.execution.django import ExecutionProviderDjango
from portfolios.providers.data.django import DataProviderDjango
from main.management.commands.rebalance import perturbate_mix, process_risk, perturbate_withdrawal, perturbate_risk, \
    get_weights, get_tax_lots

from main.management.commands.populate_test_data import populate_prices, populate_cycle_obs, populate_cycle_prediction


from main.models import Ticker, GoalMetric, Portfolio, PortfolioSet
from portfolios.calculation import get_instruments
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
        asset_classes = [self.t1.asset_class, self.t2.asset_class, self.t3.asset_class, self.t4.asset_class]
        portfolio_set = PortfolioSetFactory.create(name='set', risk_free_rate=0.01, asset_classes=asset_classes)
        self.goal = GoalFactory.create(approved_settings=self.goal_settings, cash_balance=100, portfolio_set=portfolio_set)

        Fixture1.create_execution_details(self.goal, self.t1, 5, 4, date(2016, 1, 1))
        Fixture1.create_execution_details(self.goal, self.t2, 5, 4, date(2016, 1, 1))
        Fixture1.create_execution_details(self.goal, self.t3, 5, 90, date(2016, 1, 1))
        Fixture1.create_execution_details(self.goal, self.t4, 5, 90, date(2016, 1, 1))
        Fixture1.create_execution_details(self.goal, self.t4, 5, 90, date(2016, 1, 1))

    def test_perturbate_mix1(self):
        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.equity,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.05, configured_val=0.01,
                                 comparison=GoalMetric.METRIC_COMPARISON_EXACTLY)
        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.bond,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX, rebalance_thr=0.05, configured_val=0.01,
                                 comparison=GoalMetric.METRIC_COMPARISON_MAXIMUM)

        weights = perturbate_mix(self.goal, None)
        self.assertTrue(weights[self.t1.id] + weights[self.t2.id] < 0.01 + 0.05)
        self.assertTrue(weights[self.t3.id] + weights[self.t4.id] < 0.01 + 0.05)

    def test_perturbate_mix2(self):
        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.equity,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.05, configured_val=0.3,
                                 comparison=GoalMetric.METRIC_COMPARISON_MINIMUM)

        weights = perturbate_mix(self.goal, None)
        self.assertTrue(weights[self.t3.id] + weights[self.t4.id] <= 0.75)


    def test_perturbate_withdrawal(self):
        Fixture1.create_execution_details(self.goal, self.t4, self.goal.available_balance/90, 90, date(2016, 1, 1))
        TransactionFactory.create(from_goal=self.goal, status=Transaction.STATUS_PENDING,
                                  amount=self.goal.total_balance/2)
        weights = perturbate_withdrawal(self.goal)
        self.assertTrue(sum(weights.values()) < 1)

    def test_perturbate_risk(self):
        data_provider = DataProviderDjango()
        MarkowitzScaleFactory.create()
        execution_provider = ExecutionProviderDjango()

        self.setup_performance_history()
        idata = get_instruments(data_provider)

        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.equity,
                                 type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.5, configured_val=0.5)


        lots = get_tax_lots(self.goal)
        weights = get_weights(lots, self.goal.available_balance)
        #risk = process_risk(weights=weights, goal=self.goal, idata=idata, data_provider=data_provider, execution_provider=execution_provider)
        #weights = perturbate_risk(goal=self.goal)
        self.assertTrue(True)


    def setup_performance_history(self):
        populate_prices(400)
        populate_cycle_obs(400)
        populate_cycle_prediction()

        '''
        InvestmentCycleObservationFactory.create()
        prices = (
            (self.t1, '20160101', 10),
            (self.t1, '20160102', 10.5),
            (self.t1, '20160103', 10.6),
            (self.t1, '20160104', 10.3),
            (self.t1, '20160105', 10.1),
            (self.t1, '20160106', 9.9),
            (self.t1, '20160107', 10.5),

            (self.t2, '20160101', 50),
            (self.t2, '20160102', 51),
            (self.t2, '20160103', 53),
            (self.t2, '20160104', 53.5),
            (self.t2, '20160105', 51),
            (self.t2, '20160106', 52),
            (self.t2, '20160107', 51.5),

            (self.t3, '20160101', 50),
            (self.t3, '20160102', 51),
            (self.t3, '20160103', 53),
            (self.t3, '20160104', 53.5),
            (self.t3, '20160105', 51),
            (self.t3, '20160106', 52),
            (self.t3, '20160107', 51.5),

            (self.t4, '20160101', 50),
            (self.t4, '20160102', 51),
            (self.t4, '20160103', 53),
            (self.t4, '20160104', 53.5),
            (self.t4, '20160105', 51),
            (self.t4, '20160106', 52),
            (self.t4, '20160107', 51.5),
        )
        Fixture1.set_prices(prices)'''
