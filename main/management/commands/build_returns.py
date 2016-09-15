import logging
from datetime import datetime, timedelta

import pandas as pd
from django.db.models.query import QuerySet
from django.core.management.base import BaseCommand

# The largest acceptable daily return. Anything above this will be filtered out and replaced with an average.
LARGEST_DAILY_RETURN = 0.5

logger = logging.getLogger("build_returns")


def first_consec_index(series):
    """
    Return label for the first value that produces a consecutive run with the last value.
    returns None if last value in the series is Null/None
    :param series: The series to find the first consecutive index for.
    """
    if len(series) == 0:
        return None

    mask = pd.notnull(series.values[::-1])
    i = mask.argmin()
    if i == 0:
        return None

    if mask[i]:
        return series.index[0]
    else:
        return series.index[len(series) - i]


def get_prices(instrument, dates):
    '''
    Returns cleaned weekday prices for the given instrument and date range.
    :param instrument:
    :param dates:
    :return:
    '''
    # Get the weekday prices for the instrument
    frame = instrument.daily_prices.filter(
        date__range=(dates[0] - timedelta(days=1), dates[-1]))

    #to_timeseries only works with django-pandas from QuerySet. We might be sending DataFrame already with different data_provider
    if isinstance(frame, QuerySet):
        frame = frame.to_timeseries(fieldnames=['price'], index='date')

    frame = frame.reindex(dates)

    # Remove negative prices and fill missing values
    # We replace negs with None so they are interpolated.
    prices = frame['price']
    prices[prices <= 0] = None
    # 1 back and forward is only valid with pandas 17 :(
    #prices = frame['price'].replace(frame['price'] < 0, None).interpolate(method='time', limit=1, limit_direction='both')
    return prices.interpolate(method='time', limit=2)


def get_price_returns(instrument, dates):
    """
    Get the longest consecutive daily returns series from the end date based of the availability of daily prices.
    :param instrument:
    :param dates:
    :return:
    """
    prices = get_prices(instrument, dates)
    consec = prices[prices.first_valid_index():prices.last_valid_index()]
    consec = consec[first_consec_index(consec):]

    if consec.count() != consec.size:
        emsg = "Not generating full returns for instrument: {}. " \
               "Generating longest, most recent consecutive run available from {} - {}"
        logger.warn(emsg.format(instrument.id, consec.index[0], consec.index[-1]))

    # Convert the prices to returns
    rets = consec.pct_change()[1:]

    # Remove any outlandish returns.
    brets = rets.loc[rets.abs() > LARGEST_DAILY_RETURN]
    if len(brets) > 0:
        avg = rets.mean()
        emsg = "Daily returns: {} are outside our specified limit of {}%. Replacing with the average: {}"
        logger.warn(emsg.format(brets, LARGEST_DAILY_RETURN, avg))
        brets[:] = avg

    return rets


def build_fund_returns(dates):
    """
    Build the returns for the funds in our system between the given dates
    :param dates:
    :return:
    """
    pass
    #return pd.DataFrame({index.id: get_returns(index) for  in Index.objects.all()})


def build_index_returns(dates):
    """
    Build the returns for the indices in our system between the given dates
    :param dates:
    :return:
    """
    pass
    #return pd.DataFrame({index.id: get_returns(index) for index in Index.objects.all()})


def build_returns(dates):
    build_fund_returns(dates)
    build_index_returns(dates)


def parse_date(val):
    return datetime.strptime(val, '%Y%m%d').date()


class Command(BaseCommand):
    help = 'Populates Return tables for the given dates.'

    def add_arguments(self, parser):
        parser.add_argument('begin_date', type=parse_date, help='Inclusive start date to load the data for. (YYYYMMDD)')
        parser.add_argument('end_date', type=parse_date, help='Inclusive end date to load the data for. (YYYYMMDD)')

    def handle(self, *args, **options):
        dates = pd.bdate_range(optinos['begin_date'], options['end_date'])
        build_returns(dates)
