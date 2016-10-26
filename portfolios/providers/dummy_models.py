from __future__ import unicode_literals

import uuid
import types
import copy
import functools
import numpy as np
import pandas as pd
from datetime import date, timedelta

from .execution.abstract import State
from portfolios.returns import get_price_returns
from common.structures import ChoiceEnum
from collections import defaultdict


class AssetClassMock(object):
    def __init__(self, name):
        self.name = name
        self.id = name

    def __str__(self):
        return self.name


class TickerMock(object):
    class DailyPrices(object):
        def __init__(self, daily_prices):
            self.daily_prices = daily_prices

        def filter(self, date__range):
            frame = pd.DataFrame(data=self.daily_prices.values, columns=['price'], index=self.daily_prices.index)
            frame = frame[date__range[0]:date__range[1]]
            return frame

        def last(self):
            if self.daily_prices.values.any():
                return self.daily_prices.values[-1]
            else:
                return np.NaN

    def __init__(self, symbol, daily_prices, asset_class=None, region=None, ethical=False, features=[], unit_price=10.0):
        self.symbol = symbol
        self.id = symbol
        self.asset_class = asset_class
        self.region = region
        self.ethical = ethical
        self.features = features
        self.daily_prices = self.DailyPrices(daily_prices)
        self.unit_price = unit_price

    def get_returns(self, start_date, end_date):
        return get_price_returns(self, start_date, end_date)

    def get_returns(self, dates):
        return get_price_returns(self, dates)

    def __str__(self):
        return self.symbol


class ContentType(object):
    def __init__(self, id):
        self.id = id


class PortfolioSetMock(object):
    def __init__(self, name, asset_classes, views):
        self.name = name
        self.id = name
        self.asset_classes = asset_classes
        self.views = views

    def __str__(self):
        return self.name

    def get_views_all(self):
        return self.views


class ViewMock(object):
    def __init__(self, q, assets):
        self.q = q
        self.assets = assets


class AssetFeatureValueMock(object):
    def __init__(self, name, feature=None, tickers=None):
        self.name = name
        self.id = name
        self.feature = feature
        self.assets = tickers #why would somebody name this field assets and not tickers

    def __str__(self):
        return self.name


class ClientAccount(object):
    def __init__(self, primary_owner):
        self.primary_owner = primary_owner


class GoalMock(object):
    def __init__(self, name, account, active_settings, current_balance,
                 portfolio_set=None, positions=None, data_provider=None):
        self.name = name
        self.account = account
        self.active_settings = active_settings
        self.approved_settings = self.active_settings
        self.portfolio_set = portfolio_set
        self.current_balance = self.cash_balance = current_balance
        self.position_lots = positions
        self.sale = list()
        self.data_provider = data_provider

    def total_balance(self):
        return self.current_balance

    def get_positions_all(self):
        positions = defaultdict(float)
        prices = defaultdict(float)
        for p in self.position_lots:
            positions[p.execution_distribution.execution.ticker.id] += p.quantity
            prices[p.execution_distribution.execution.ticker.id] = p.price

        pos = list()
        for id, quantity in positions.items():
            position = dict()
            position['ticker_id'] = id
            position['quantity'] = quantity
            position['price'] = prices[id]
            pos.append(position)
        return pos

    def get_lots_all(self):
        lots = list()
        for l in self.position_lots:
            lot = dict()
            lot['ticker_id'] = l.execution_distribution.execution.ticker.id
            lot['quantity'] = l.quantity
            lot['price'] = l.execution_distribution.execution.price
            lot['executed'] = l.execution_distribution.execution.executed
            lots.append(lot)
        return lots

    def get_lots_symbol(self, symbol):
        lots = list()
        all_lots = self.get_lots_all()
        for l in all_lots:
            if l['ticker_id'] == symbol:
                lots.append(l)
        return lots

    @property
    def available_balance(self):
        balance = 0
        for position in self.get_positions_all():
            balance += position['quantity'] * position['price']
        return balance + self.cash_balance

    def __str__(self):
        return '[' + self.name + " : " + self.account.primary_owner


class PositionLot(object):
    def __init__(self, quantity, price, ticker, executed):
        self.quantity = quantity
        self.execution_distribution = types.SimpleNamespace()
        self.execution_distribution.execution = types.SimpleNamespace()
        self.execution_distribution.transaction = types.SimpleNamespace()
        self.execution_distribution.execution.price = price
        self.execution_distribution.execution.ticker = ticker
        self.execution_distribution.execution.executed = executed
        self.execution_distribution.transaction.from_goal = None
        self.data_provider = None

    @property
    def price(self):
        if self.data_provider is not None:
            ticker = self.data_provider.get_ticker(self.execution_distribution.execution.ticker.id)
        return float(ticker.daily_prices.last())


    @property
    def value(self):
        return float(self.quantity * self.price)


class Sale(object):
    def __init__(self, ticker, price, quantity):
        self.ticker = ticker
        self.price = price
        self.quantity = quantity


class GoalSettingMock(object):
    def __init__(self, id, metric_group, portfolio=None, goal=None):
        self.id = id
        self.metric_group = metric_group
        self.portfolio = portfolio
        self.goal = goal

    def constraint_inputs(self):
        """
        A comparable set of inputs to all the optimisation constraints that would be generated from this group.
        :return:
        """
        features = {}
        for metric in self.get_metrics_all():
            if metric.type == GoalMetricMock.METRIC_TYPE_RISK_SCORE:
                risk = metric.configured_val
            else:
                features[metric.feature] = (metric.comparison, metric.feature, metric.configured_val)
        return risk, features

    def __str__(self):
        return u'Goal Settings #%s (%s)' % (self.id, self.portfolio)

    def get_metrics_all(self):
        return self.metric_group.metrics

    def get_portfolio_items_all(self):
        return self.portfolio.items


class GoalMetricGroupMock(object):
    def __init__(self, metrics):
        self.metrics = metrics


class GoalMetricMock(object):
    METRIC_TYPE_PORTFOLIO_MIX = 0
    METRIC_TYPE_RISK_SCORE = 1
    metric_types = {
        METRIC_TYPE_PORTFOLIO_MIX: 'Portfolio Mix',
        METRIC_TYPE_RISK_SCORE: 'RiskScore'
    }

    def __init__(self, type, feature, rebalance_type, configured_val, comparison):
        self.type = type
        self.feature = feature
        self.rebalance_type = rebalance_type
        self.configured_val = configured_val
        self.comparison = comparison


class PortfolioMock(object):
    def __init__(self, id, stdev, er, items=None):
        self.id = id
        self.stdev = stdev
        self.er = er
        self.items = items or []

    def __str__(self):
        return u'Portfolio #%s' % self.id


class PortfolioItemMock(object):
    def __init__(self, asset, weight, volatility):
        self.asset = asset
        self.weight = weight
        self.volatility = volatility


class MarkowitzScaleMock(object):
    def __init__(self, date, min, max, a, b, c):
        self.date = date
        self.min = min
        self.max = max
        self.a = a
        self.b = b
        self.c = c


class MarketOrderRequestMock(object):
    def __init__(self, account, state=None):
        self.state = state
        self.account = account
        self.execution_requests = []
        self.executions = []

    def __str__(self):
        return "[{}] - {}".format(self.account, State(self.state).name)


class ExecutionRequestMock(object):
    def __init__(self, reason=None, goal=None, asset=None, volume=None,
                 order=None, limit_price=None):
        self.reason = reason
        self.id = uuid.uuid4()
        self.goal = goal
        self.asset = asset
        self.volume = volume
        self.order = order
        self.limit_price = limit_price


class ExecutionMock(object):
    def __init__(self, asset, volume, order, price, executed, amount):
        self.asset = asset
        self.volume = volume
        self.order = order
        self.price = price
        self.executed = executed
        self.amount = amount


class InvestmentCycleObservationMock(object):
    class Cycle(ChoiceEnum):
        EQ = (0, 'eq')
        EQ_PK = (1, 'eq_pk')
        PK_EQ = (2, 'pk_eq')
        EQ_PIT = (3, 'eq_pit')
        PIT_EQ = (4, 'pit_eq')

    def __init__(self, as_of, cycle):
        self.as_of = as_of
        self.cycle = cycle


class InvestmentCyclePredictionMock(object):
    def __init__(self, as_of, eq, eq_pk, pk_eq, eq_pit, pit_eq):
        _check_numbers(min=0, max=1, numbers=[eq, eq_pk, pk_eq, eq_pit, pit_eq])

        self.as_of = as_of
        self.eq = eq
        self.eq_pk = eq_pk
        self.pk_eq = pk_eq
        self.eq_pit = eq_pit
        self.pit_eq = pit_eq


def _check_numbers(min, max, numbers):
    for n in numbers:
        if n < min or n > max:
            raise Exception("number not between 0 and 1")


class InvestmentCycleObservationFactory(object):
    @staticmethod
    def create_cycles():
        observations = list()
        observations.append(
            InvestmentCycleObservationMock(as_of=date(2011, 1, 1), cycle=InvestmentCycleObservationMock.Cycle.EQ_PIT.value))
        observations.append(
            InvestmentCycleObservationMock(as_of=date(2011, 1, 5), cycle=InvestmentCycleObservationMock.Cycle.PIT_EQ.value))
        observations.append(
            InvestmentCycleObservationMock(as_of=date(2011, 1, 7), cycle=InvestmentCycleObservationMock.Cycle.EQ.value))
        observations.append(
            InvestmentCycleObservationMock(as_of=date(2011, 1, 11), cycle=InvestmentCycleObservationMock.Cycle.EQ_PK.value))
        observations.append(
            InvestmentCycleObservationMock(as_of=date(2011, 1, 13), cycle=InvestmentCycleObservationMock.Cycle.PK_EQ.value))
        observations.append(
            InvestmentCycleObservationMock(as_of=date(2011, 1, 15), cycle=InvestmentCycleObservationMock.Cycle.EQ.value))
        observations.append(
            InvestmentCycleObservationMock(as_of=date(2011, 1, 18), cycle=InvestmentCycleObservationMock.Cycle.EQ_PIT.value))
        observations.append(
            InvestmentCycleObservationMock(as_of=date(2011, 1, 20), cycle=InvestmentCycleObservationMock.Cycle.PIT_EQ.value))
        return observations

    @staticmethod
    def create_predictions():
        predictions = list()
        vals = [
            [0.08089787, 0.167216193, 0.007325566, 0.143641463, 0.733230633],
            [0.080636192, 0.151937142, 0.187936638, 0.39640021, 0.420692639],
            [0.087140048, 0.122145455, 0.043799137, 0.508127278, 0.412764823],
            [0.086595196, 0.163545905, 0.029313429, 0.329095078, 0.370009886],
            [0.087243834, 0.19905742, 0.00229681, 0.09144718, 0.390732573],
            [0.081566295, 0.277402407, 0.080812535, 0.045212519, 0.360884538],
            [0.07358428, 0.117376517, 0.001417166, 0.143329684, 0.395081559],
            [0.073802749, 0.133804588, 0.000635776, 0.394104881, 0.39465102],
            [0.075446787, 0.082311401, 0.000812869, 0.271816537, 0.69018451],
            [0.078041426, 0.244725389, 0.014591784, 0.049618232, 0.472784413],
            [0.076303139, 0.115293179, 0.176512979, 0.07634871, 0.375165155],
            [0.073802749, 0.133804588, 0.000635776, 0.394104881, 0.39465102],
        ]
        dt = date(2011, 1, 1)
        for p in vals:
            predictions.append(
                InvestmentCyclePredictionMock(as_of=dt, eq=p[0], eq_pk=p[1], pk_eq=p[2], eq_pit=p[3], pit_eq=p[4])
            )
            dt += timedelta(days=31)
        return predictions


class InstrumentsFactory(object):
    @staticmethod
    def create_ticker(ticker, daily_prices, benchmark_id, benchmark_daily_prices):
        asset_class_mock = AssetClassMock("equity")
        ticker_mock = TickerMock(symbol=ticker, daily_prices=daily_prices,
                                 asset_class=asset_class_mock)
        ticker_mock.benchmark = TickerMock(symbol=benchmark_id, daily_prices=benchmark_daily_prices)
        ticker_mock.benchmark_content_type = ContentType(benchmark_id)
        ticker_mock.benchmark_object_id = ''
        return ticker_mock

    @staticmethod
    @functools.lru_cache(maxsize=100)
    def create_tickers():
        fund_price_matrix = pd.read_csv('fundPrices_mock.csv', index_col='Date', infer_datetime_format=True,
                                             parse_dates=True)
        fund_price_matrix.index.name = 'date'
        tickers = list(fund_price_matrix.columns)
        benchmark_id = tickers #list of benchmark IDs, in same order as fundPriceMatrix. for now, fund is equal to its benchmark
        benchmark_price_matrix = fund_price_matrix #for now, fund is equal to its benchmark

        tickerMocks = []
        for ticker, benchmark_id in zip(tickers, benchmark_id):
            ticker_mock = InstrumentsFactory.create_ticker(ticker=ticker,
                                                           daily_prices=fund_price_matrix[ticker],
                                                           benchmark_id=benchmark_id,
                                                           benchmark_daily_prices=benchmark_price_matrix[benchmark_id])
            tickerMocks.append(ticker_mock)
        return tickerMocks

    @staticmethod
    def get_fund_price_matrix():
        tickers = InstrumentsFactory.create_tickers()
        matrix = None
        for ticker in tickers:
            current = pd.DataFrame(data=ticker.daily_prices.daily_prices.values,
                                   index=ticker.daily_prices.daily_prices.index,
                                   columns=[ticker.id])
            if matrix is None:
                matrix = current
            else:
                matrix = pd.concat([matrix, current], axis=1)
        return matrix

    @staticmethod
    def get_dates():
        tickers = InstrumentsFactory.get_fund_price_matrix()
        timedates = tickers.index.to_pydatetime()
        dates = [timedate.date() for timedate in timedates]
        return dates


class GoalFactory(object):
    @staticmethod
    def create_goal(data_provider):
        asset_feature_value = AssetFeatureValueMock(name='featureName', feature=None, tickers=['EEM', 'EEMV', 'EFA'])
        goal_metric = [GoalMetricMock(type=GoalMetricMock.METRIC_TYPE_RISK_SCORE, feature=asset_feature_value,
                                      rebalance_type="1", configured_val=0.0, comparison=2)]
        goal_metric_group = GoalMetricGroupMock(metrics=goal_metric)

        portfolio_items = []
        tickers = InstrumentsFactory.create_tickers()
        for ticker in tickers:
            portfolio_items.append(PortfolioItemMock(asset=ticker, weight=0.1, volatility=0))
        portfolio_items = portfolio_items
        portfolio = PortfolioMock(id='portfolio', er=0, stdev=0, items=portfolio_items)
        goal_settings = GoalSettingMock(id="goal_settings_id", metric_group=goal_metric_group, portfolio=portfolio)
        views = [ViewMock(q=0.1, assets='EEM,EEMV\n1,-1'),
                 ViewMock(q=0.2, assets='EEM,EFA\n1,-1'),
                 ViewMock(q=0.3, assets='EEMV,EFA\n1,-1')]

        portfolio_set = PortfolioSetMock(name='portfolio_set1',
                                         asset_classes=[AssetClassMock("equity"),
                                                        AssetClassMock("fixed Income")],
                                         views=views)
        #positions = [PositionMock(ticker=tickers[0], share=3), PositionMock(ticker=tickers[1], share=4)]
        positions = []
        account = ClientAccount(primary_owner="Jozef Rudy")
        goal = GoalMock(name="buy_car",
                        account=account,
                        current_balance=10000,
                        active_settings=goal_settings,
                        portfolio_set=portfolio_set,
                        positions=positions,
                        data_provider=data_provider)

        goal_non_nested = copy.copy(goal)
        goal_non_nested.active_settings = None
        goal.approved_settings.goal = goal_non_nested

        return goal
