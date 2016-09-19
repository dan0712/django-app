import logging
from datetime import timedelta

import numpy as np

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.timezone import now

from main.models import MarketIndex, DailyPrice, MarketCap, Ticker

logger = logging.getLogger("populate_test_prices")


def random_walk(N, delta):
    """
    Use numpy.cumsum and numpy.random.uniform to generate
    a one dimensional random walk of length N, each step with a random delta between +=delta.
    """
    return np.cumsum(np.random.uniform(-delta, delta, N))


def delete_data():
    DailyPrice.objects.all().delete()
    MarketCap.objects.all().delete()


def populate_prices(days):
    prices = []
    today = now().today()

    # Do the prices and market caps for the indices
    for ind in MarketIndex.objects.all():
        delta = np.random.uniform(1, 5)
        ps = random_walk(days, delta)
        initial = np.random.uniform(100, 200)
        if ps[-1] < 0:
            initial += -ps[-1]
        ps += initial
        for i, p in enumerate(ps):
            prices.append(DailyPrice(instrument=ind, date=today - timedelta(days=i+1), price=p))
        MarketCap.objects.create(instrument=ind, date=today, value=np.random.uniform(10000000, 50000000000000))

    # Do the prices for the funds
    for fund in Ticker.objects.all():
        delta = np.random.uniform(1, 5)
        ps = random_walk(days, delta)
        initial = np.random.uniform(100, 200)
        if ps[-1] < 0:
            initial += -ps[-1]
        ps += initial
        prices.append(DailyPrice(instrument=fund, date=today, price=p))
        for i, p in enumerate(ps):
            prices.append(DailyPrice(instrument=fund, date=today - timedelta(days=i+1), price=p))

    DailyPrice.objects.bulk_create(prices)


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
        resp = input('The database you are connected to is: {}|{}|{}. Are you sure? y/N: '.format(connection.settings_dict['ENGINE'],
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
        print("Done.")
