from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

from django.utils import timezone
from django.test import TestCase

from api.v1.tests.factories import GoalSettingFactory, GoalMetricFactory, GoalFactory, TickerFactory, \
    AssetFeatureValueFactory, PortfolioSetFactory, MarkowitzScaleFactory, MarketIndexFactory, AssetClassFactory, AssetFeatureFactory
from main.management.commands.populate_test_data import populate_prices, populate_cycle_obs, populate_cycle_prediction, \
    delete_data
from main.models import GoalMetric
from portfolios.calculation import calc_opt_inputs, build_instruments, calculate_portfolio, calculate_portfolio_old
from portfolios.providers.data.django import DataProviderDjango
from portfolios.providers.execution.django import ExecutionProviderDjango

mocked_now = datetime(2016, 1, 1)


class CalculationTest(TestCase):

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_calc_opt_inputs_no_assets_for_constraint(self):
        """
        Makes sure when we have no assets filling a constraint, we behave appropriately.
        """

        # This fund has a different feature to the one in the mix metric, but it is in the correct portfolio set.
        fund1 = TickerFactory.create()
        AssetFeatureValueFactory.create(assets=[fund1])
        ps1 = PortfolioSetFactory.create(asset_classes=[fund1.asset_class])

        # Create a settings object with a metric for a feature with no instruments in the current portfolio set.
        feature = AssetFeatureValueFactory.create()
        settings = GoalSettingFactory.create()
        risk_metric = GoalMetricFactory.create(group=settings.metric_group)
        mix_metric = GoalMetricFactory.create(group=settings.metric_group,
                                              type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                                              feature=feature,
                                              comparison=GoalMetric.METRIC_COMPARISON_MAXIMUM,
                                              configured_val=.3)
        goal = GoalFactory.create(selected_settings=settings, portfolio_set=ps1)

        # The below fund has the desired feature, but is not in the goal's portfolio set.
        fund2 = TickerFactory.create()
        feature.assets.add(fund2)

        # Create some instrument data for the two assets
        self.m_scale = MarkowitzScaleFactory.create()
        # populate the data needed for the prediction
        # We need at least 500 days as the cycles go up to 70 days and we need at least 7 cycles.
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())
        data_provider = DataProviderDjango()
        idata = build_instruments(data_provider)

        execution_provider = ExecutionProviderDjango()

        # Get the opt inputs, there should be no constraint for the max for the feature with no funds.
        result = calc_opt_inputs(settings=settings,
                                 idata=idata,
                                 data_provider=data_provider,
                                 execution_provider=execution_provider)
        xs, lam, constraints, settings_instruments, settings_symbol_ixs, lcovars = result
        self.assertEqual(len(constraints), 3)  # All positive, and sum to 1

        # Then create a fund in the portfolio I want. We should get a constraint for the maximum for the feature.
        fund3 = TickerFactory.create(asset_class=fund1.asset_class)
        feature.assets.add(fund3)
        delete_data()
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())
        idata = build_instruments(data_provider)
        result = calc_opt_inputs(settings=settings,
                                 idata=idata,
                                 data_provider=data_provider,
                                 execution_provider=execution_provider)
        xs, lam, constraints, settings_instruments, settings_symbol_ixs, lcovars = result
        self.assertEqual(len(constraints), 4)  # All positive, sum to 1, and the max constraint

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_calculate_portfolio_old(self):
        fund0 = TickerFactory.create(symbol='IAGG')
        fund1 = TickerFactory.create(symbol='ITOT')
        fund2 = TickerFactory.create(symbol='VEA')
        fund0 = TickerFactory.create(symbol='IPO')
        fund3 = TickerFactory.create(symbol='EEM')
        fund4 = TickerFactory.create(symbol='AGG')

        AssetFeatureValueFactory.create(assets=[fund1, fund2, fund3, fund4])
        ps1 = PortfolioSetFactory \
            .create(asset_classes=[fund1.asset_class, fund2.asset_class, fund3.asset_class, fund4.asset_class])

        # Create a settings object with a metric for a feature with no instruments in the current portfolio set.
        feature = AssetFeatureValueFactory.create()
        settings = GoalSettingFactory.create()
        risk_metric = GoalMetricFactory.create(group=settings.metric_group)
        mix_metric = GoalMetricFactory.create(group=settings.metric_group,
                                              type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
                                              feature=feature,
                                              comparison=GoalMetric.METRIC_COMPARISON_MAXIMUM,
                                              configured_val=.3)
        goal = GoalFactory.create(selected_settings=settings, portfolio_set=ps1)

        # The below fund has the desired feature, but is not in the goal's portfolio set.

        feature.assets.add(fund1)

        # Create some instrument data for the two assets
        self.m_scale = MarkowitzScaleFactory.create()
        # populate the data needed for the prediction
        # We need at least 500 days as the cycles go up to 70 days and we need at least 7 cycles.
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())
        data_provider = DataProviderDjango()
        execution_provider = ExecutionProviderDjango()
        idata = build_instruments(data_provider)
        result = calculate_portfolio_old(settings=settings,
                                         data_provider=data_provider,
                                         execution_provider=execution_provider,
                                         idata=idata)
        self.assertTrue(True)

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_calculate_portfolio(self):
        # TODO
        # constraints -> limit them -> maximum minimum value of 5%, maximum max value of 95%

        asset_class1 = AssetClassFactory.create(name='US_TOTAL_BOND_MARKET')
        asset_class2 = AssetClassFactory.create(name='HEDGE_FUNDS')

        fund0 = TickerFactory.create(symbol='IAGG', asset_class=asset_class1)
        fund1 = TickerFactory.create(symbol='ITOT', asset_class=asset_class2)
        fund0 = TickerFactory.create(symbol='IPO')
        fund6 = TickerFactory.create(symbol='rest')

        ps1 = PortfolioSetFactory \
            .create(asset_classes=[asset_class1, asset_class2, fund6.asset_class])

        #feature = AssetFeatureValueFactory.create()
        #feature.assets.add(fund6)
        settings = GoalSettingFactory.create()
        risk_metric = GoalMetricFactory.create(group=settings.metric_group, type=GoalMetric.METRIC_TYPE_RISK_SCORE)
        #mix_metric = GoalMetricFactory.create(group=settings.metric_group,
        #                                      type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX,
        #                                      feature=feature,
        #                                      comparison=GoalMetric.METRIC_COMPARISON_MAXIMUM,
        #                                      )
        goal = GoalFactory.create(selected_settings=settings, portfolio_set=ps1)



        # Create some instrument data for the two assets
        self.m_scale = MarkowitzScaleFactory.create()

        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())
        data_provider = DataProviderDjango()
        execution_provider = ExecutionProviderDjango()
        idata = build_instruments(data_provider)
        result = calculate_portfolio(settings=settings,
                                     data_provider=data_provider,
                                     execution_provider=execution_provider,
                                     idata=idata)
        self.assertTrue(True)
