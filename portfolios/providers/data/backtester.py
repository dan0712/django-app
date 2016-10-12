from collections import defaultdict
from datetime import timedelta
import pandas as pd
import numpy as np
from portfolios.providers.dummy_models import AssetClassMock, \
    AssetFeatureValueMock, InstrumentsFactory, MarkowitzScaleMock, \
    PortfolioSetMock, InvestmentCycleObservationFactory
from portfolios.returns import get_prices
from .abstract import DataProviderAbstract
from portfolios.exceptions import OptimizationException


class DataProviderBacktester(DataProviderAbstract):
    def __init__(self, sliding_window_length):
        self.sliding_window_length = sliding_window_length
        self.cache = None
        self.markowitz_scale = None
        self.tickers = list()
        self.benchmark_marketweight_matrix = pd.read_csv('capitalization_mock.csv',
                                                         index_col='Date',
                                                         infer_datetime_format=True,
                                                         parse_dates=True)
        self.portfolio_sets = [PortfolioSetMock(name='portfolio_set1',
                                                asset_classes=[AssetClassMock("equity"),
                                                               AssetClassMock("fixed Income")],
                                                views=None
                                                )]
        self.asset_feature_values = [AssetFeatureValueMock(name='featureName',
                                                           feature=None,
                                                           tickers=['EEM', 'EEMV', 'EFA'])]
        self.tickers = InstrumentsFactory.create_tickers()
        self.dates = InstrumentsFactory.get_dates()
        self.__current_date = self.sliding_window_length
        self.time_constrained_tickers = []
        self.investment_cycles = InvestmentCycleObservationFactory.create_cycles()
        self.investment_predictions = InvestmentCycleObservationFactory.create_predictions()

    def move_date_forward(self):
        # this function is only used in backtesting
        self.cache = None
        success = False
        if len(self.dates) > self.__current_date + 1:
            self.__current_date += 1
            success = True
        else:
            print("cannot move date forward")
        return success

    def get_current_date(self):
        date = self.dates[self.__current_date]
        return date

    def get_start_date(self):
        date = self.dates[self.__current_date - self.sliding_window_length]
        return date

    def get_fund_price_latest(self, ticker):
        prices = get_prices(ticker, self.get_start_date(), self.get_current_date())
        prices = prices.irow(-1)
        return prices

    def get_features(self, ticker):
        return ticker.features

    def get_asset_class_to_portfolio_set(self):
        ac_ps = defaultdict(list)
        for ps in self.portfolio_sets:
            for ac in ps.asset_classes:
                ac_ps[ac.id].append(ps.id)
        return ac_ps

    def get_tickers(self):
        self.time_constrained_tickers = []
        for ticker in self.tickers:
            date_range = (self.get_current_date() - timedelta(days=self.sliding_window_length),
                          self.get_current_date())

            ticker = InstrumentsFactory.create_ticker(ticker=ticker.symbol,
                                                      daily_prices=ticker.daily_prices.filter(date__range=date_range),
                                                      benchmark_id=ticker.benchmark.symbol,
                                                      benchmark_daily_prices=
                                                      ticker.benchmark.daily_prices.filter(date__range=date_range)
                                                      )
            self.time_constrained_tickers.append(ticker)
        return self.time_constrained_tickers

    def get_ticker(self, tid):
        ticker = None
        for t in self.time_constrained_tickers:
            if t.id == tid:
                ticker = t
                break
        return ticker

    def get_market_weight(self, content_type_id, content_object_id):
        # provide market cap for a given benchmark at a given date (latest available) - use get_current_date
        mp = self.benchmark_marketweight_matrix.ix[:self.get_current_date(), content_type_id]
        if mp.shape[0] > 0:
            mp = mp.irow(-1)
        else:
            mp = None
        return None if mp is None else mp

    def get_portfolio_sets_ids(self):
        return [val.id for val in self.portfolio_sets]

    def get_asset_feature_values_ids(self):
        return [val.id for val in self.asset_feature_values]

    def get_goals(self):
        return

    def get_markowitz_scale(self):
        if self.markowitz_scale is None:
            self.set_markowitz_scale(date=self.get_current_date(), min=-1, max=1, a=1, b=2, c=3)
        return self.markowitz_scale

    def set_markowitz_scale(self, date, mn, mx, a, b, c):
        self.markowitz_scale = MarkowitzScaleMock(date, mn, mx, a, b, c)

    def get_instrument_cache(self):
        return self.cache

    def set_instrument_cache(self, data):
        self.cache = data

    def get_investment_cycles(self):
        obs = self.investment_cycles
        if not obs:
            raise OptimizationException("There are no historic observations available")
        return self.investment_cycles

    def get_last_cycle_start(self):
        obs = self.get_cycle_obs()
        # Populate the cache as we'll be hitting it a few times. Boolean evaluation causes full cache population

        # Get the investment cycle for the current date
        current_cycle = obs[-1]

        if len(obs) < 2:
            raise Exception("There are less than 2 investment cycles")
        # Get the end date of the last non-current cycle before the current one
        pre_dt = obs.index[-2]

        # Get the end date of the previous time the current cycle was
        idx = int(np.where(obs[:pre_dt][:-1] == current_cycle)[-1])
        pre_on_dt = obs.index[idx]

        # Get the end date of the time before that when we were not in the current cycle
        observations = obs[:pre_on_dt][:-1]
        observations = observations[observations != current_cycle]
        pre_off_dt = observations.index[-1]

        # Not get the first date after this when the current cycle was on and we have the answer
        return obs[pre_off_dt:].index[0]

    def get_cycle_obs(self, begin_date=None):
        cycles = self.investment_cycles

        if begin_date is None:
            begin_date = cycles[0].as_of

        data = pd.Series()
        for cycle in cycles:
            if cycle.as_of >= begin_date:
                observation = pd.Series(cycle.cycle, index=[cycle.as_of])
                data = data.append(observation)
        return data

    def get_probs_df(self, begin_date):
        predictions = self.investment_predictions
        data = pd.DataFrame(columns=['eq', 'eq_pk', 'pk_eq', 'eq_pit', 'pit_eq'])
        for p in predictions:
            if p.as_of >= begin_date:
                row = pd.DataFrame(data=[[p.eq,p.eq_pk,p.pk_eq,p.eq_pit,p.pit_eq]],  index=[p.as_of], columns=['eq', 'eq_pk', 'pk_eq', 'eq_pit', 'pit_eq'])
                data = data.append(row)
        return data


    def get_investment_cycle_predictions(self):
        pass

