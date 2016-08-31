from datetime import date
from unittest.mock import Mock

from django.test import TestCase
from statsmodels.stats.correlation_tools import cov_nearest

from main.models import Region, AssetClass, View, Ticker, DailyPrice, MarketCap
from portfolios.management.commands.portfolio_calculation_pure import *


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
        DailyPrice.objects.create(symbol='ASS', price='1.1', date=date(2015, 1, 31))
        DailyPrice.objects.create(symbol='ASS', price='1.2', date=date(2015, 2, 28))
        DailyPrice.objects.create(symbol='ASS', price='1.3', date=date(2015, 3, 31))
        DailyPrice.objects.create(symbol='ASS', price='1.4', date=date(2015, 4, 30))
        DailyPrice.objects.create(symbol='USB', price='2.1', date=date(2015, 1, 31))
        DailyPrice.objects.create(symbol='USB', price='2.2', date=date(2015, 2, 28))
        DailyPrice.objects.create(symbol='USB', price='2.3', date=date(2015, 3, 31))
        DailyPrice.objects.create(symbol='USB', price='2.4', date=date(2015, 4, 30))
        DailyPrice.objects.create(symbol='USB1', price='3.4', date=date(2015, 1, 31))
        DailyPrice.objects.create(symbol='USB1', price='3.3', date=date(2015, 2, 28))
        DailyPrice.objects.create(symbol='USB1', price='3.2', date=date(2015, 3, 31))
        DailyPrice.objects.create(symbol='USB1', price='3.1', date=date(2015, 4, 30))
        DailyPrice.objects.create(symbol='AUMS', price='1.1', date=date(2015, 1, 31))
        DailyPrice.objects.create(symbol='AUMS', price='1.1', date=date(2015, 2, 28))
        DailyPrice.objects.create(symbol='AUMS', price='1.1', date=date(2015, 3, 31))
        DailyPrice.objects.create(symbol='AUMS', price='1.2', date=date(2015, 4, 30))
        MarketCap.objects.create(value=self._mkt_caps[0], ticker=Ticker.objects.get(symbol='ASS'))
        MarketCap.objects.create(value=self._mkt_caps[1], ticker=Ticker.objects.get(symbol='USB'))
        MarketCap.objects.create(value=self._mkt_caps[2], ticker=Ticker.objects.get(symbol='USB1'))
        MarketCap.objects.create(value=self._mkt_caps[3], ticker=Ticker.objects.get(symbol='AUMS'))
        self._covars, self._samples, self._instruments, self._masks = build_instruments(DataProviderDjango())
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
        self.assertListEqual(get_market_weights(self._instruments[[True, True, True, True]]).values.tolist(),
                             [0.20130932896890344, 0.7463175122749591, 0.019639934533551555, 0.03273322422258593])
        # Test Mask. Make sure index and values are good.
        w = get_market_weights(self._instruments[[True, False, True, False]])
        self.assertListEqual(w.index.tolist(), ['ASS', 'USB1'])
        self.assertListEqual(w.values.tolist(), [0.9111111111111111, 0.08888888888888889])

    def test_get_constraints_auto(self):
        # Check auto allocation mode, non ethical.
        goal1 = Mock(Goal)
        goal1.optimization_mode = 1
        goal1.picked_regions = '["UK", "AU"]'
        goal1.allocation = 0.4
        goal1.satellite_pct = 0.2
        goal1.type = "INVESTING"

        # Create the goal masks and check there's only 2 instruments active,
        goal_symbol_ixs, cvx_masks = get_settings_masks(goal1, self._masks)
        self.assertEqual(goal_symbol_ixs, [0, 3])

        # Create the core constraints and make sure it's of the correct number of variables.
        xs, constraints = get_core_constraints(len(goal_symbol_ixs))
        self.assertEqual(xs.size, (2, 1))

        # Create the allocation constraints and check there are only the constraints needed.
        constraints += get_metric_constraints(goal1, cvx_masks, xs)
        self.assertEqual(len(constraints), 4)

    def test_get_constraints_explicit_ethical(self):
        # Check explicit allocation mode, ethical.
        goal2 = Mock(Goal)
        goal2.name = 'ethical_test'
        goal2.optimization_mode = 2
        goal2.region_sizes = {'AU': 1.0}
        goal2.allocation = 0.0
        goal2.satellite_pct = 1.0
        goal2.type = "INVESTING_ETHICAL"

        # Create the goal masks and check there's only one instrument active, and it's the ethical aussie one.
        goal_symbol_ixs, cvx_masks = get_settings_masks(goal2, self._masks)
        self.assertEqual(goal_symbol_ixs, [3])

        # Create the core constraints and make sure it's of the correct number of variables.
        xs, constraints = get_core_constraints(len(goal_symbol_ixs))
        self.assertEqual(xs.size, (1, 1))

        # Create the allocation constraints and check there are only the constraints needed.
        # no allocation or satellite constraint as they're not needed due to goal_mask.
        constraints += get_allocation_constraints(goal2, cvx_masks, xs)
        self.assertEqual(len(constraints), 4)

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
        goal1.picked_regions = '["UK", "AU"]'
        goal1.allocation = 1.0  # Have to do full stock allocation, as there are no bonds to work with for this goal
        goal1.satellite_pct = 0.2
        goal1.type = "INVESTING"
        view_models = [Mock(View), Mock(View)]
        view_models[0].q = .1
        view_models[0].assets = 'ASS,USB\n1,-1'
        view_models[1].q = .2
        view_models[1].assets = 'AUMS,USB\n1,-1'
        goal1.portfolio_set.views.all.return_value = view_models
        goal1.total_balance = 60000
        idata = get_instruments()
        portfolio, er, var = calculate_portfolio(goal1, idata)
        self.assertEqual(len(portfolio), 2)
        self.assertAlmostEquals(portfolio['AU_STOCKS'], 0.8)
        self.assertAlmostEquals(portfolio['AU_STOCK_MUTUALS'], 0.2)

    def test_calculate_portfolios(self):
        goal1 = Mock(Goal)
        goal1.name = "Goal 1"
        goal1.optimization_mode = 1
        goal1.picked_regions = '["UK", "AU"]'
        goal1.allocation = 0.23
        goal1.satellite_pct = 0.2
        goal1.type = "INVESTING"
        view_models = [Mock(View), Mock(View)]
        view_models[0].q = .1
        view_models[0].assets = 'ASS,USB\n1,-1'
        view_models[1].q = .2
        view_models[1].assets = 'AUMS,USB\n1,-1'
        goal1.portfolio_set.views.all.return_value = view_models
        goal1.total_balance = 60000
        portfolios = calculate_portfolios(goal1)
        for key, val in portfolios.items():
            if key == '1.00':
                self.assertAlmostEquals(val['volatility'], 11.1206)
                self.assertAlmostEquals(val['risk'], 1.0)
                self.assertAlmostEquals(val['expectedReturn'], 138.56)
                self.assertEquals(len(val['allocations']), 2)
                self.assertAlmostEquals(val['allocations']['AU_STOCKS'], 0.8)
                self.assertAlmostEquals(val['allocations']['AU_STOCK_MUTUALS'], 0.2)
            else:
                self.assertIsNone(val['volatility'])
                self.assertIsNone(val['expectedReturn'])
                self.assertEquals(val['allocations'], {})
                self.assertIsNone(val['risk'])
        # Our original allocation should be reinstated.
        self.assertEqual(goal1.allocation, 0.23)

    def test_psd_norm(self):
        data = {'AAXJ': [66.029999000000004, 63.0, 59.270000000000003, 53.340000000000003, 52.75],
                'UBU': [20.079999999999998, 20.079999999999998, 21.550000000000001, 20.559999999999999, 20.18],
                'ALD': [45.939999, 45.330002, 44.490001999999997, 42.729999999999997, 42.409999999999997],
                'VSO': [47.399999999999999, 42.899999999999999, 43.340000000000003, 41.719999999999999, 40.950000000000003],
                'VAS': [73.700000000000003, 69.989999999999995, 72.099999999999994, 66.569999999999993, 64.549999999999997],
                'BTWJPNF_AU': [0.66000000000000003, 0.66000000000000003, 0.68999999999999995, 0.67000000000000004, 0.63],
                'VGS': [59.75, 58.439999999999998, 61.0, 58.25, 56.780000000000001],
                'EMB': [112.370003, 109.91999800000001, 109.660004, 108.010002, 106.400002],
                'FTAL': [41.854999999999997, 39.329999999999998, 40.390000000000001, 38.32, 37.229999999999997],
                'UBP': [20.150717539569801, 19.1999999999999, 19.050000000000001, 17.990000000000101, 17.240000000000101],
                'BTWASHF_AU': [1.8799999999999999, 1.8400000000000001, 1.8799999999999999, 1.8400000000000001, 1.8400000000000001],
                'VLC': [64.719999999999999, 61.219999999999999, 63.530000000000001, 57.469999999999999, 55.170000000000002],
                'MCHI': [59.849997999999999, 56.040000999999997, 50.040000999999997, 44.099997999999999, 43.810001],
                'UBE': [20.983828369806702, 20.140000000000001, 21.510000000000002, 20.1099999999999, 19.75],
                'BTA0420_AU': [1.1799999999999999, 1.1299999999999999, 1.0700000000000001, 1.02, 1.0],
                'SLXX': [136.13999999999999, 131.22, 134.57499999999999, 130.71000000000001, 131.46000000000001],
                'VTS': [143.81, 139.49000000000001, 149.49000000000001, 143.16, 139.47],
                'RGB': [21.379999999999999, 21.0, 21.280000000000001, 21.399999999999999, 21.52],
                'IJP': [17.239999999999998, 16.710000000000001, 17.68, 16.98, 16.09],
                'HOW0062_AU': [1.05, 1.05, 1.0, 1.01, 1.02],
                'DSUM': [24.91, 24.739999999999998, 24.510000000000002, 23.040001, 23.559999000000001],
                'ILB': [115.41, 113.8, 114.0, 114.56, 114.31999999999999],
                'PEBIX_US': [9.9499999999999993, 10.529999999999999, 10.19, 10.1, 9.7400000000000002],
                'BTWFAUS_AU': [1.74, 1.6499999999999999, 1.73, 1.5900000000000001, 1.5600000000000001],
                'BTWEUSH_AU': [1.3200000000000001, 1.29, 1.3799999999999999, 1.3500000000000001, 1.3200000000000001],
                'IEAG': [87.209999999999994, 83.355000000000004, 84.674999999999997, 87.055000000000007, 87.405000000000001],
                'RSM': [20.789999999999999, 20.550000000000001, 20.77, 20.850000000000001, 20.629999999999999],
                'ROTHWSE_AU': [2.6400000000000001, 2.4700000000000002, 2.3999999999999999, 2.3300000000000001, 2.3900000000000001],
                'UBA': [19.886842423199901, 18.6400000000001, 19.129999999999999, 17.440000000000001, 16.879999999999999],
                'IUSB': [101.769997, 100.519997, 100.459999, 100.389999, 100.25],
                'ROTHFXD_AU': [1.23, 1.21, 1.1899999999999999, 1.21, 1.21],
                'UBJ': [20.763995359855802, 20.479000000000099, 21.379999999999999, 20.549999999999901, 19.469999999999999],
                'IEU': [61.130000000000003, 57.57, 61.130000000000003, 58.340000000000003, 56.100000000000001],
                'VGE': [62.549999999999997, 60.229999999999997, 58.549999999999997, 53.600000000000001, 52.880000000000003],
                'RIGS': [25.25, 24.940000999999999, 24.940000999999999, 24.549999, 24.100000000000001],
                'VHY': [69.030000000000001, 65.040000000000006, 64.150000000000006, 59.219999999999999, 57.100000000000001],
                'UBW': [21.244103679132198, 20.510000000000002, 21.620000000000001, 19.779999999999902, 20.079999999999998],
                'BOND': [26.280000000000001, 25.800000000000001, 26.030000000000001, 26.23, 26.02],
                'BTWAMSH_AU': [1.23, 1.21, 1.24, 1.21, 1.1799999999999999]}
        df = pd.DataFrame(data)
        df_cov = df.cov()
        #print(df_cov)
        p1 = cov_nearest(df_cov)
        #print(p1-df_cov)
