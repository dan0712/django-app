import logging
from copy import copy
from datetime import timedelta, date

import numpy as np
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.timezone import now

from api.v1.tests.factories import InvestmentCycleObservationFactory, InvestmentCyclePredictionFactory
from main.models import MarketIndex, DailyPrice, MarketCap, Ticker, InvestmentCycleObservation, \
    InvestmentCyclePrediction, Inflation

logger = logging.getLogger("populate_test_prices")


def random_walk(n, delta):
    """
    Use numpy.cumsum and numpy.random.uniform to generate
    a one dimensional random walk of length N, each step with a random delta between +=delta.
    """
    return np.cumsum(np.random.uniform(-delta, delta, n))


def delete_data():
    DailyPrice.objects.all().delete()
    MarketCap.objects.all().delete()
    InvestmentCycleObservation.objects.all().delete()
    InvestmentCyclePrediction.objects.all().delete()
    Inflation.objects.all().delete()


def populate_prices(days, asof=now().date()):
    """
    Populate days worth of test prices as of the given asof date
    :param days: Number of historic prices to populate
    :param asof: The Date to finish the population
    :return:
    """
    prices = []

    # Do the prices and market caps for the indices
    for ind in MarketIndex.objects.all():
        delta = np.random.uniform(0, 5)
        ps = random_walk(days, delta)
        initial = abs(min(ps)) + 1
        ps += initial
        for i, p in enumerate(ps):
            prices.append(DailyPrice(instrument=ind, date=asof - timedelta(days=i), price=p))
        MarketCap.objects.create(instrument=ind, date=asof, value=np.random.uniform(10000000, 50000000000000))

    # Do the prices for the funds
    for fund in Ticker.objects.all():
        delta = np.random.uniform(0, 5)
        ps = random_walk(days, delta)
        initial = abs(min(ps)) + 1
        ps += initial
        for i, p in enumerate(ps):
            prices.append(DailyPrice(instrument=fund, date=asof - timedelta(days=i), price=p))
    DailyPrice.objects.bulk_create(prices)


def populate_cycle_obs(days, asof=now().date()):
    # do not input less than 400 days, method might fail
    cycle = int(np.random.uniform(0, 6))
    prog = [0, 1, 2, 0, 3, 4]
    dt = asof - timedelta(days=days)
    while days:
        run = min(int(np.random.uniform(20, 50)), days)
        while run:
            InvestmentCycleObservationFactory.create(as_of=dt, cycle=prog[cycle])
            dt += timedelta(days=1)
            run -= 1
            days -= 1
        cycle += 1
        cycle %= 6


def populate_cycle_prediction(asof=now().date()):
    InvestmentCyclePredictionFactory.create(as_of=asof - timedelta(days=1),
                                            eq=0.3,
                                            eq_pk=0.4,
                                            pk_eq=0.2,
                                            eq_pit=0.1,
                                            pit_eq=0.6)


def populate_inflation(asof=now().date(), value=0.001):
    """
    Populate monthly inflation figures in the DB. Calculates forward 100 years from the asof date
    :param asof:
    :param value: The monthly inflation to use.
    :return:
    """

    # Populate some inflation figures.
    inflations = []
    for i in range(1200):
        dt = asof + relativedelta(months=i)
        inflations.append(Inflation(year=dt.year, month=dt.month, value=value))
    if hasattr(Inflation, '_cum_data'):
        del Inflation._cum_data
    Inflation.objects.bulk_create(inflations)


class Command(BaseCommand):
    help = ('Populates random walk test instrument price data. '
            'NUKES DailyPrice and MarketCap TABLES AND REPLACES WITH RANDOM, TIMELY DATA')

    def add_arguments(self, parser):
        parser.add_argument('--yes_i_am_really_sure',
                            action='store_true',
                            required=True,
                            help='Do you REALLY want to do this?')
        parser.add_argument('--clear_only',
                            action='store_true',
                            help='Only clear out the existing values, do not populate')

    def handle(self, *args, **options):
        istr = 'The database you are connected to is: {}|{}|{}. Are you sure? y/N: '
        resp = input(istr.format(connection.settings_dict['ENGINE'],
                                 connection.settings_dict['HOST'],
                                 connection.settings_dict['NAME']))
        if resp.lower() != 'y':
            print("Returning with DB unchanged.")
            return

        # Known seed so tests are reproducible, although we'd have to fix the variable date aspect as well.
        np.random.seed(1234567890)

        print("Deleting data.")
        delete_data()
        if not options['clear_only']:
            print("Repopulating.")
            populate_prices(400)
            populate_cycle_obs(400)
            populate_cycle_prediction()
            populate_inflation(asof=date(2016, 1, 1))
        print("Done.")
