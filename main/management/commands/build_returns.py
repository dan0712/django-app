import datetime
import logging

import pandas as pd

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


def get_prices(instrument, begin_date, end_date):
    '''
    Returns cleaned weekday prices for the given instrument and date range.
    :param instrument:
    :param begin_date:
    :param end_date:
    :return:
    '''
    # Get the weekday prices for the instrument
    pqs = instrument.daily_prices.filter(date__range=(begin_date - datetime.timedelta(days=1), end_date))
    frame = pqs.to_timeseries(fieldnames=['price'], index='date').reindex(pd.bdate_range(begin_date, end_date))

    # Remove negative prices and fill missing values
    # We replace negs with None so they are interpolated.
    prices = frame['price']
    prices[prices <= 0] = None
    # 1 back and forward is only valid with pandas 17 :(
    #prices = frame['price'].replace(frame['price'] < 0, None).interpolate(method='time', limit=1, limit_direction='both')
    return prices.interpolate(method='time', limit=2)


def get_price_returns(instrument, begin_date, end_date):
    """
    Get the longest consecutive daily returns series from the end date based of the availability of daily prices.
    :param instrument:
    :param begin_date:
    :param end_date:
    :return:
    """
    prices = get_prices(instrument, begin_date, end_date)
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


def build_fund_returns(begin_date, end_date):
    """
    Build the returns for the funds in our system between the given dates
    :param begin_date:
    :param end_date:
    :return:
    """
    pass
    #return pd.DataFrame({index.id: get_returns(index) for  in Index.objects.all()})


def build_index_returns(begin_date, end_date):
    """
    Build the returns for the indices in our system between the given dates
    :param begin_date:
    :param end_date:
    :return:
    """
    pass
    #return pd.DataFrame({index.id: get_returns(index) for index in Index.objects.all()})


def build_returns(begin_date, end_date):
    build_fund_returns(begin_date, end_date)
    build_index_returns(begin_date, end_date)


def parse_date(val):
    return datetime.datetime.strptime(val, '%Y%m%d').date()


class Command(BaseCommand):
    help = 'Populates Return tables for the given dates.'

    def add_arguments(self, parser):
        parser.add_argument('begin_date', type=parse_date, help='Inclusive start date to load the data for. (YYYYMMDD)')
        parser.add_argument('end_date', type=parse_date, help='Inclusive end date to load the data for. (YYYYMMDD)')

    def handle(self, *args, **options):
        build_returns(options['begin_date'], options['end_date'])
