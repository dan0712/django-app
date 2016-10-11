from datetime import date, timedelta
from unittest.mock import MagicMock

import numpy as np
import pandas as pd

from django.test import TestCase

from api.v1.tests.factories import InvestmentCycleObservationFactory, InvestmentCyclePredictionFactory, \
    DailyPriceFactory, TickerFactory
from main.models import InvestmentCycleObservation
from portfolios.exceptions import OptimizationException
from portfolios.prediction.investment_clock import InvestmentClock, CYCLE_LABEL
from portfolios.providers.data.django import DataProviderDjango


class InvestmentClockTest(TestCase):
    def setUp(self):
        self.data_provider = DataProviderDjango()
        self.data_provider.get_current_date = MagicMock(return_value=date(2016, 2, 1))
        self.last_cycle_start = date(2016, 1, 5)
        self.last_cycle_end = date(2016, 1, 14)  # The last day before the observed next cycle
        # We need to have a full range of cycle plus at least one date behind.
        InvestmentCycleObservationFactory.create(as_of=date(2016, 1, 1),
                                                 cycle=InvestmentCycleObservation.Cycle.EQ_PIT.value)
        InvestmentCycleObservationFactory.create(as_of=self.last_cycle_start,
                                                 cycle=InvestmentCycleObservation.Cycle.PIT_EQ.value)
        InvestmentCycleObservationFactory.create(as_of=date(2016, 1, 7),
                                                 cycle=InvestmentCycleObservation.Cycle.EQ.value)
        InvestmentCycleObservationFactory.create(as_of=date(2016, 1, 11),
                                                 cycle=InvestmentCycleObservation.Cycle.EQ_PK.value)
        InvestmentCycleObservationFactory.create(as_of=date(2016, 1, 13),
                                                 cycle=InvestmentCycleObservation.Cycle.PK_EQ.value)
        InvestmentCycleObservationFactory.create(as_of=date(2016, 1, 15),
                                                 cycle=InvestmentCycleObservation.Cycle.EQ.value)
        InvestmentCycleObservationFactory.create(as_of=date(2016, 1, 18),
                                                 cycle=InvestmentCycleObservation.Cycle.EQ_PIT.value)
        InvestmentCycleObservationFactory.create(as_of=date(2016, 1, 20),
                                                 cycle=InvestmentCycleObservation.Cycle.PIT_EQ.value)
        self.predictor = InvestmentClock(self.data_provider)

    def populate_returns(self):
        t1 = TickerFactory.create()
        p1 = [1.01, 1.02, 1.03, 1.04, 1.03, 1.05, 1.03, 1.03, 1.04, 1.05, 1.06, 1.07, 1.09, 1.11, 1.13, 1.12]
        t2 = TickerFactory.create()
        p2 = [6.01, 5.92, 6.03, 6.04, 5.93, 5.95, 5.93, 5.87, 5.84, 5.80, 5.78, 5.74, 5.79, 5.76, 5.73, 5.7]
        t3 = TickerFactory.create()
        p3 = [101.01, 101.02, 100.03, 101.04, 101.63, 102.05, 102.03, 101.93, 102.34, 102.55, 103, 102.67, 102.9, 103.11, 102.23, 101.12]
        days = [1, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22]
        for i, day in enumerate(days):
            dt = date(2016, 1, day)
            DailyPriceFactory.create(instrument=t1.benchmark, date=dt, price=p1[i])
            DailyPriceFactory.create(instrument=t2.benchmark, date=dt, price=p2[i])
            DailyPriceFactory.create(instrument=t3.benchmark, date=dt, price=p3[i])

    def populate_probabilities(self):
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
        dt = date(2016, 1, 1)
        for p in vals:
            InvestmentCyclePredictionFactory.create(as_of=dt, eq=p[0], eq_pk=p[1], pk_eq=p[2], eq_pit=p[3], pit_eq=p[4])
            dt += timedelta(days=31)

    def test_get_latest_history_date(self):
        last_start = self.predictor.get_last_cycle_start()
        self.assertEqual(last_start, self.last_cycle_start)

    def test_get_normalized_probabilities(self):
        self.populate_probabilities()
        norm_probs = self.predictor.get_normalized_probabilities(date(2000, 1, 1))
        self.assertEqual(len(norm_probs), 1)  # Only get the results up to our current_date
        # make sure the first one has the correct values
        self.assertAlmostEqual(norm_probs.iloc[0, 0], 0.071445, 6)
        self.assertAlmostEqual(norm_probs.iloc[0, 1], 0.147677, 6)
        self.assertAlmostEqual(norm_probs.iloc[0, 2], 0.006470, 6)
        self.assertAlmostEqual(norm_probs.iloc[0, 3], 0.126857, 6)
        self.assertAlmostEqual(norm_probs.iloc[0, 4], 0.647552, 6)

    def test_get_fund_predictions(self):
        self.populate_probabilities()
        self.populate_returns()
        mu, sigma = self.predictor.get_fund_predictions()
        self.assertAlmostEqual(mu[1], 2.689327, 6)
        self.assertAlmostEqual(mu[2], -0.345612, 6)
        self.assertAlmostEqual(mu[3], -0.297295, 6)

    def test_get_fund_predictions_no_returns(self):
        self.populate_probabilities()
        with self.assertRaises(OptimizationException):
            self.predictor.get_fund_predictions()

    def test_expected_returns_prob_v1(self):
        probs = np.array((0.1, 0.15, 0.25, 0.1, 0.4)).reshape((1, 5))
        data = [
            [0.01,  0.00, 0],
            [0.02,  0.00, 0],
            [0.01,  0.01, 1],
            [0.02,  0.01, 1],
            [0.01, -0.02, 2],
            [0.02, -0.01, 2],
            [0.01,  0.00, 0],
            [0.02,  0.00, 0],
            [0.01, -0.03, 3],
            [0.02, -0.03, 3],
            [0.01,  0.04, 4],
            [0.01,  0.04, 4],
        ]
        df = pd.DataFrame(data,
                          index=pd.date_range('1/1/2011', periods=12, freq='b'),
                          columns=['A', 'B', CYCLE_LABEL])

        # Average simple returns in phases for A are:
        # 0: (1.01 * 1.02 * 1.01 * 1.02) ** (1/4) = 1.01498768
        # 1: (1.01 * 1.02) ** (1/2) = 1.01498768
        # 2: (1.01 * 1.02) ** (1/2) = 1.01498768
        # 3: (1.01 * 1.02) ** (1/2) = 1.01498768
        # 4: (1.01 * 1.01) ** (1/2) = 1.01

        # Probability weighted
        # 1.01498768 * 0.1 + 1.01498768 * 0.15 + 1.01498768 * 0.25 + 1.01498768 * 0.1 + 1.01 * 0.4 = 1.012992608

        # Average simple returns in phases for B are:
        # 0: (1.0 * 1.0 * 1.0 * 1.0) ** (1/4) = 1.0
        # 1: (1.01 * 1.01) ** (1/2) = 1.01
        # 2: (0.98 * 0.99) ** (1/2) = 0.9849873
        # 3: (0.97 * 0.97) ** (1/2) = 0.97
        # 4: (1.04 * 1.04) ** (1/2) = 1.04

        # Probability weighted simple returns for B
        # 1.0 * 0.1 + 1.01 * 0.15 + 0.9849873 * 0.25 + 0.97 * 0.1 + 1.04 * 0.4 = 1.010746825

        # Just to prove the math works, average converted log returns in phases for B are the same as those calculated
        # for simple returns:
        # 0: exp((log(1.0) + log(1.0) + log(1.0) + log(1.0)) / 4) = 1.0
        # 1: exp((log(1.01) + log(1.01)) / 2) = 1.01
        # 2: exp((log(0.98) + log(0.99)) / 2) = 0.9849873
        # 3: exp((log(0.97) + log(0.97)) / 2) = 0.97
        # 4: exp((log(1.04) + log(1.04)) / 2) = 1.04

        returns = self.predictor._expected_returns_prob_v1(df, probs)
        self.assertAlmostEqual(returns['A'], 0.012993, 6)
        self.assertAlmostEqual(returns['B'], 0.010747, 6)