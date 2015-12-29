from datetime import date
from django.test import TestCase
from unittest.mock import Mock, patch
import pandas as pd
from main.models import Region, Ticker, AssetClass, Goal, MonthlyPrices
from portfolios.models import View, MarketCap
from portfolios.management.commands.portfolio_calculation import *


class PortfolioCalculationTests(TestCase):
    def setUp(self):
        Region.objects.create(name="AU")
        Region.objects.create(name="UK")
        Region.objects.create(name="US")
        AssetClass.objects.create(name="US_BONDS", investment_type='BONDS', display_order=1)
        AssetClass.objects.create(name="AU_STOCKS", investment_type='STOCKS', display_order=2)
        AssetClass.objects.create(name="AU_STOCK_MUTUALS", investment_type='STOCKS', display_order=3)
        Ticker.objects.create(symbol="ASS",
                              display_name='AU Stock 1',
                              ethical=False,
                              region=Region.objects.get(name="AU"),
                              asset_class=AssetClass.objects.get(name='AU_STOCKS'),
                              ordering=1)
        Ticker.objects.create(symbol="USB",
                              display_name='US Bond 1',
                              ethical=True,
                              region=Region.objects.get(name="US"),
                              asset_class=AssetClass.objects.get(name='US_BONDS'),
                              ordering=1)
        Ticker.objects.create(symbol="USB1",
                              display_name='US Bond 2',
                              ethical=False,
                              region=Region.objects.get(name="US"),
                              asset_class=AssetClass.objects.get(name='US_BONDS'),
                              ordering=1)
        Ticker.objects.create(symbol="AUMS",
                              display_name='AU Mutual Stocks 1',
                              ethical=True,
                              region=Region.objects.get(name="AU"),
                              asset_class=AssetClass.objects.get(name='AU_STOCK_MUTUALS'),
                              etf=False,
                              ordering=1)
        self._mkt_caps = [123000000, 456000000, 12000000, 20000000]
        '''
        self._api = Mock(DbApi)
        self._api.get_all_prices.side_effect = [pd.Series([1.1, 1.2, 1.3, 1.4], name='ASS'),
                                                pd.Series([2.1, 2.2, 2.3, 2.4], name='USB'),
                                                pd.Series([3.4, 3.3, 3.2, 3.1], name='USB1'),
                                                pd.Series([1.1, 1.1, 1.1, 1.2], name='AUMS')]
        '''
        MonthlyPrices.objects.create(symbol='ASS', price='1.1', date=date(2015, 1, 31))
        MonthlyPrices.objects.create(symbol='ASS', price='1.2', date=date(2015, 2, 28))
        MonthlyPrices.objects.create(symbol='ASS', price='1.3', date=date(2015, 3, 31))
        MonthlyPrices.objects.create(symbol='ASS', price='1.4', date=date(2015, 4, 30))
        MonthlyPrices.objects.create(symbol='USB', price='2.1', date=date(2015, 1, 31))
        MonthlyPrices.objects.create(symbol='USB', price='2.2', date=date(2015, 2, 28))
        MonthlyPrices.objects.create(symbol='USB', price='2.3', date=date(2015, 3, 31))
        MonthlyPrices.objects.create(symbol='USB', price='2.4', date=date(2015, 4, 30))
        MonthlyPrices.objects.create(symbol='USB1', price='3.4', date=date(2015, 1, 31))
        MonthlyPrices.objects.create(symbol='USB1', price='3.3', date=date(2015, 2, 28))
        MonthlyPrices.objects.create(symbol='USB1', price='3.2', date=date(2015, 3, 31))
        MonthlyPrices.objects.create(symbol='USB1', price='3.1', date=date(2015, 4, 30))
        MonthlyPrices.objects.create(symbol='AUMS', price='1.1', date=date(2015, 1, 31))
        MonthlyPrices.objects.create(symbol='AUMS', price='1.1', date=date(2015, 2, 28))
        MonthlyPrices.objects.create(symbol='AUMS', price='1.1', date=date(2015, 3, 31))
        MonthlyPrices.objects.create(symbol='AUMS', price='1.2', date=date(2015, 4, 30))
        MarketCap.objects.create(value=self._mkt_caps[0], ticker=Ticker.objects.get(symbol='ASS'))
        MarketCap.objects.create(value=self._mkt_caps[1], ticker=Ticker.objects.get(symbol='USB'))
        MarketCap.objects.create(value=self._mkt_caps[2], ticker=Ticker.objects.get(symbol='USB1'))
        MarketCap.objects.create(value=self._mkt_caps[3], ticker=Ticker.objects.get(symbol='AUMS'))
        self._covars, self._samples, self._instruments, self._masks = build_instruments()
        self._expected_returns = [1.6243024031751947, 0.7059826278890338, -0.308913087739887, 0.43080261749853954]
        #print(self._covars)
        #print(self._instruments)
        #print(self._masks)

    def test_get_instruments(self):
        self.assertEqual(self._samples, 4)
        self.assertListEqual(self._instruments['mkt_cap'].values.tolist(), self._mkt_caps)
        self.assertListEqual(self._instruments['exp_ret'].values.tolist(), self._expected_returns)

    def test_get_initial_weights(self):
        # Test all active
        self.assertListEqual(get_initial_weights(self._instruments[[True, True, True, True]]).values.tolist(),
                             [0.20130932896890344, 0.7463175122749591, 0.019639934533551555, 0.03273322422258593])
        # Test Mask. Make sure index and values are good.
        w = get_initial_weights(self._instruments[[True, False, True, False]])
        self.assertListEqual(w.index.tolist(), ['ASS', 'USB1'])
        self.assertListEqual(w.values.tolist(), [0.9111111111111111, 0.08888888888888889])

    def test_get_cvx_constraints(self):
        # Check auto allocation mode, non ethical.
        goal1 = Mock(Goal)
        goal1.optimization_mode = 1
        goal1.picked_regions = ["UK", "AU"]
        goal1.allocation = 0.4
        goal1.satellite_pct = 0.2
        goal1.type = "INVESTING"
        xs, goal_mask, constraints = get_cvx_constraints(goal1, self._masks)
        self.assertEqual(xs.size, (2,1))  # Only 2 instruments active
        self.assertEqual(goal_mask[0].values.tolist(), [True, False, False, True])
        self.assertEqual(len(constraints), 4)  # for allocation and satellite pct, all=1, allpos

        # Check explicit allocation mode, ethical.
        goal2 = Mock(Goal)
        goal2.name = 'ethical_test'
        goal2.optimization_mode = 2
        goal2.region_sizes = {'AU': 0.4}
        goal2.allocation = 0.0
        goal2.satellite_pct = 1.0
        goal2.type = "INVESTING_ETHICAL"
        xs, goal_mask, constraints = get_cvx_constraints(goal2, self._masks)
        self.assertEqual(xs.size, (1,1))  # Only one instrument active
        self.assertEqual(goal_mask[0].values.tolist(), [False, False, False, True])
        # for all=1, allpos, each of the 2 instruments, and ethical -- no allocation or satellite constraint as they're not needed due to goal_mask.
        self.assertEqual(len(constraints), 5)

    def test_get_views(self):
        goal1 = Mock(Goal)
        goal1.name = "Goal 1"
        view_models = [Mock(View), Mock(View), Mock(View)]
        view_models[0].q = .1
        view_models[0].assets = 'ASS,USB\n1,-1'
        view_models[1].q = .2
        view_models[1].assets = 'AUMS,USB\n1,-1'
        view_models[2].q = .3
        view_models[2].assets = 'USB1,USB\n1,-1'
        goal1.portfolio_set.views.all.return_value = view_models
        views, view_rets = get_views(goal1, self._instruments[self._masks[ETF_MASK_NAME]])
        self.assertEqual(views.tolist(), [[1.0, -1.0, 0.0], [0.0, -1.0, 1.0]])
        self.assertEqual(view_rets.tolist(), [0.1, 0.3])

    def test_calculate_portfolio(self):
        goal1 = Mock(Goal)
        goal1.name = "Goal 1"
        goal1.optimization_mode = 1
        goal1.picked_regions = ["UK", "AU"]
        goal1.allocation = 1.0
        #goal1.allocation = 0.8 # Cannot do 20% bonds, as there are no bonds...
        goal1.satellite_pct = 0.2
        goal1.type = "INVESTING"
        view_models = [Mock(View), Mock(View)]
        view_models[0].q = .1
        view_models[0].assets = 'ASS,USB\n1,-1'
        view_models[1].q = .2
        view_models[1].assets = 'AUMS,USB\n1,-1'
        goal1.portfolio_set.views.all.return_value = view_models
        idata = get_instruments()
        portfolio, er, var = calculate_portfolio(goal1, idata)
        print(portfolio, er, var)

    def test_calculate_portfolios(self):
        goal1 = Mock(Goal)
        goal1.name = "Goal 1"
        goal1.optimization_mode = 1
        goal1.picked_regions = ["UK", "AU"]
        goal1.allocation = 0.23
        goal1.satellite_pct = 0.2
        goal1.type = "INVESTING"
        view_models = [Mock(View), Mock(View)]
        view_models[0].q = .1
        view_models[0].assets = 'ASS,USB\n1,-1'
        view_models[1].q = .2
        view_models[1].assets = 'AUMS,USB\n1,-1'
        goal1.portfolio_set.views.all.return_value = view_models
        # We should only get an allocation for 100% stocks.
        print(calculate_portfolios(goal1))
        self.assertEqual(goal1.allocation, 0.23)

    '''
    def test_calculate_portfolio(self):
        goal1 = Mock(Goal)
        goal1.name = "Goal 1"
        goal1.optimization_mode = 1
        goal1.picked_regions = ["UK", "AU"]
        goal1.allocation = 0.4
        goal1.satellite_pct = 0.2
        goal1.type = "INVESTING"
        view_models = [Mock(View), Mock(View)]
        view_models[0].q = .1
        view_models[0].assets = 'ASS,USB\n1,-1'
        view_models[1].q = .2
        view_models[1].assets = 'AUMS,USB\n1,-1'
        goal1.portfolio_set.views.all.return_value = view_models
        portfolio = calculate_portfolio(goal1)
        print(portfolio)
    '''