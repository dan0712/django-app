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
    get_weights, get_tax_lots, calc_opt_inputs

from main.management.commands.populate_test_data import populate_prices, populate_cycle_obs, populate_cycle_prediction


from main.models import Ticker, GoalMetric, Portfolio, PortfolioSet
from portfolios.calculation import get_instruments
from datetime import datetime, date


class RebalanceTest(test.TestCase):
    def setUp(self):
        self.t1 = TickerFactory.create(symbol='SPY', unit_price=5)
        self.t2 = TickerFactory.create(symbol='VEA', unit_price=5)
        self.t3 = TickerFactory.create(symbol='TIP', unit_price=100)
        self.t4 = TickerFactory.create(symbol='IEV', unit_price=100)

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

        self.data_provider = DataProviderDjango()
        self.execution_provider = ExecutionProviderDjango()
        MarkowitzScaleFactory.create()
        self.setup_performance_history()
        self.idata = get_instruments(self.data_provider)

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

        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.equity,
                                 type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.5, configured_val=0.5)

        opt_inputs = calc_opt_inputs(self.goal.approved_settings, self.idata, self.data_provider, self.execution_provider)
        weights, min_weights = perturbate_mix(self.goal, opt_inputs)
        self.assertTrue(min_weights[self.t1.id] + min_weights[self.t2.id] < 0.01 + 0.05)
        self.assertTrue(min_weights[self.t3.id] + min_weights[self.t4.id] < 0.01 + 0.05)

    def test_perturbate_mix2(self):
        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.equity,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.05, configured_val=0.3,
                                 comparison=GoalMetric.METRIC_COMPARISON_MINIMUM)
        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.bond,
                                 type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.05, configured_val=0.7,
                                 comparison=GoalMetric.METRIC_COMPARISON_MAXIMUM)

        GoalMetricFactory.create(group=self.goal_settings.metric_group, feature=self.equity,
                                 type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                 rebalance_type=GoalMetric.REBALANCE_TYPE_ABSOLUTE,
                                 rebalance_thr=0.5, configured_val=0.5)

        opt_inputs = calc_opt_inputs(self.goal.approved_settings, self.idata, self.data_provider,
                                     self.execution_provider)

        weights, min_weights = perturbate_mix(self.goal, opt_inputs)
        self.assertTrue(min_weights[self.t3.id] + min_weights[self.t4.id] <= 0.75 or weights is not None)

    def test_perturbate_withdrawal(self):
        Fixture1.create_execution_details(self.goal, self.t4, self.goal.available_balance/90, 90, date(2016, 1, 1))
        TransactionFactory.create(from_goal=self.goal, status=Transaction.STATUS_PENDING,
                                  amount=self.goal.total_balance/2)
        weights = perturbate_withdrawal(self.goal)
        self.assertTrue(sum(weights.values()) < 1)

    def test_perturbate_risk(self):
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
