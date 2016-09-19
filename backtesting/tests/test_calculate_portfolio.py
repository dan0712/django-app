from datetime import datetime, timedelta

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from random import randint, random
from statsmodels.stats.correlation_tools import cov_nearest

from main.models import AssetClass, DailyPrice, GoalMetric, InvestmentType, \
    MarketCap, MarketIndex, MarkowitzScale, Portfolio, PortfolioItem, Region, \
    Ticker
from main.tests.fixture import Fixture1
from portfolios.calculation import build_instruments, calculate_portfolio, \
    calculate_portfolios
from portfolios.providers.execution.django import ExecutionProviderDjango
from portfolios.providers.data.django import DataProviderDjango


class BaseTest(TestCase):
    def setUp(self):
        Region.objects.create(name="AU")
        Region.objects.create(name="UK")
        Region.objects.create(name="US")
        AssetClass.objects.create(name="US_BONDS",
                                  investment_type=InvestmentType.Standard.BONDS.get(),
                                  display_order=1)
        AssetClass.objects.create(name="AU_STOCKS",
                                  investment_type=InvestmentType.Standard.STOCKS.get(),
                                  display_order=2)
        AssetClass.objects.create(name="AU_STOCK_MUTUALS",
                                  investment_type=InvestmentType.Standard.STOCKS.get(),
                                  display_order=3)

        index = MarketIndex.objects.create(id=1,
                                           display_name='ASSIndex',
                                           region=Region.objects.get(name="AU"),
                                           currency='AUD',
                                           data_api='bloomberg',
                                           data_api_param='MI1')

        ass = Ticker.objects.create(symbol="ASS",
                                    display_name='AU Stock 1',
                                    ethical=False,
                                    region=Region.objects.get(name="AU"),
                                    asset_class=AssetClass.objects.get(name='AU_STOCKS'),
                                    ordering=1,
                                    description='some stock',
                                    benchmark=index,
                                    data_api='portfolios.api.bloomberg',
                                    data_api_param='ASS')

        ubs = Ticker.objects.create(symbol="USB",
                                    display_name='US Bond 1',
                                    ethical=True,
                                    region=Region.objects.get(name="US"),
                                    asset_class=AssetClass.objects.get(name='US_BONDS'),
                                    ordering=1,
                                    description='some stock',
                                    benchmark=index,
                                    data_api='portfolios.api.bloomberg',
                                    data_api_param='USB')
        usb1 = Ticker.objects.create(symbol="USB1",
                                     display_name='US Bond 2',
                                     ethical=False,
                                     region=Region.objects.get(name="US"),
                                     asset_class=AssetClass.objects.get(name='US_BONDS'),
                                     ordering=1,
                                     description='some stock',
                                     benchmark=index,
                                     data_api='portfolios.api.bloomberg',
                                     data_api_param='USB1')
        aums = Ticker.objects.create(symbol="AUMS",
                                     display_name='AU Mutual Stocks 1',
                                     ethical=True,
                                     region=Region.objects.get(name="AU"),
                                     asset_class=AssetClass.objects.get(name='AU_STOCK_MUTUALS'),
                                     etf=False,
                                     ordering=1,
                                     description='some stock',
                                     benchmark=index,
                                     data_api='portfolios.api.bloomberg',
                                     data_api_param='AUMS')
        assets = [ass, ubs, usb1, aums, index]

        num_days = 600
        end = datetime.today().date()
        start = end - timedelta(days=num_days)

        dates = list()
        current = start
        while end > current:
            dates.append(pd.Timestamp(current).to_datetime())
            current = current + timedelta(days=1)

        prices = [str(random()/100+1) for i in range(0, num_days)]
        self._mkt_caps = [str(randint(1000,2000)) for i in range(0, num_days)]

        for asset in assets:
            for dt, price, mkt_cap in zip(dates, prices, self._mkt_caps):
                    DailyPrice.objects.create(instrument_object_id=asset.id,
                                              instrument_content_type=ContentType.objects.get_for_model(asset),
                                              price=price,
                                              date=dt)
                    MarketCap.objects.create(instrument_object_id=asset.id,
                                             instrument_content_type=ContentType.objects.get_for_model(asset),
                                             value=mkt_cap,
                                             date=dt)
        self._data_provider = DataProviderDjango()
        self._execution_provider = ExecutionProviderDjango()
        self._covars, self._samples, self._instruments, self._masks = build_instruments(self._data_provider)
        MarkowitzScale.objects.create(date=self._data_provider.get_current_date(),
                                      min=-1,
                                      max=1,
                                      a=1,
                                      b=2,
                                      c=3)

    def test_get_instruments(self):
        #self.assertEqual(self._samples, 4)
        self.assertEqual(int(self._instruments['mkt_cap'].values[0]), int(self._mkt_caps[-1]))
        #self.assertListEqual(self._instruments['exp_ret'].values.tolist(), self._expected_returns)

    def test_calculate_portfolio(self):
        goal1 = Fixture1.goal1()
        goal1.portfolio_set.asset_classes = [
            AssetClass.objects.get(name="US_BONDS"),
            AssetClass.objects.get(name="AU_STOCKS"),
            AssetClass.objects.get(name="AU_STOCK_MUTUALS")
        ]
        goal1.selected_settings.metric_group.metrics = [GoalMetric.objects.create(group=Fixture1.metric_group1(),
                                                                                  type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                                                                  rebalance_type="1",
                                                                                  configured_val=0.0,
                                                                                  comparison=2,
                                                                                  rebalance_thr=0.05)
                                                       ]
        goal1.selected_settings.SYSTEM_CURRENCY = 'USD'
        goal1.cash_balance = 1000
        idata = self._data_provider.get_instruments()
        portfolio, er, var = calculate_portfolio(settings=goal1.selected_settings,
                                                 idata=idata,
                                                 data_provider=self._data_provider,
                                                 execution_provider=self._execution_provider)
        self.assertEqual(len(portfolio), 4)

    def test_calculate_portfolios(self):
        goal1 = Fixture1.goal1()
        goal1.portfolio_set.asset_classes = [
            AssetClass.objects.get(name="US_BONDS"),
            AssetClass.objects.get(name="AU_STOCKS"),
            AssetClass.objects.get(name="AU_STOCK_MUTUALS")
        ]
        goal1.selected_settings.metric_group.metrics = [GoalMetric.objects.create(group=Fixture1.metric_group1(),
                                                                                  type=GoalMetric.METRIC_TYPE_RISK_SCORE,
                                                                                  rebalance_type="1",
                                                                                  configured_val=0.0,
                                                                                  comparison=2,
                                                                                  rebalance_thr=0.05)
                                                       ]
        goal1.selected_settings.SYSTEM_CURRENCY = 'USD'
        goal1.cash_balance = 1000
        portfolio = Portfolio.objects.create(id=1, er=1, stdev=2, setting=goal1.selected_settings)
        PortfolioItem.objects.create(asset=Ticker.objects.get(symbol='ASS'),
                                     portfolio=portfolio,
                                     weight=0.1,
                                     volatility=0.2)
        portfolios = calculate_portfolios(goal1.selected_settings, data_provider=self._data_provider,
                                          execution_provider=self._execution_provider)
        self.assertEqual(len(portfolios), 101)

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
