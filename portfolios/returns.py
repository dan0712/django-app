# All methods relating to getting returns for instruments.
from datetime import timedelta, date
import logging

import pandas as pd
import numpy as np

from django.db.models.query import QuerySet

# The largest acceptable daily return. Anything above this will be filtered out and replaced with an average.
# This is an extremely poor way to deal with splits.
LARGEST_DAILY_RETURN = 0.48

logger = logging.getLogger('portfolios.returns')


def benchmark_uid(fund):
    return '{}_{}'.format(fund.benchmark_content_type.id, fund.benchmark_object_id)


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


def filter_returns(returns, end_tol=0, min_days=None, latest_start=None):
    """
    Results will be a consecutive time block of returns, all ending on the same day.
    The date they end on must be within 'end_tol' of the specified ending day.
    :param returns: A pandas dataframe containing the timeseries of values to filter.
    :param end_tol: The maximum number of days before last time in the frame's index that any column is allowed to end.
    :param min_days: The minimum number of days that need to be available for a column to remain in the series.
    :return: A Pandas DataFrame of series for each column meeting the data requirements.
    """
    if returns.empty:
        return returns.drop(returns.columns, axis=1)
    min_end = (returns.index[-1] - timedelta(days=end_tol)).date()
    to_drop = []
    for name, ret in returns.iteritems():
        last_dt = ret.last_valid_index()
        if last_dt is None:
            emsg = "Excluding returns column: {} as it has no returns available."
            logger.warn(emsg.format(name))
            to_drop.append(name)
            continue
        last_dt = date(last_dt.year, last_dt.month, last_dt.day)
        if last_dt < min_end:
            emsg = "Excluding returns column: {} as the last day of data is before {} (the minimum acceptable)."
            logger.warn(emsg.format(name, min_end))
            to_drop.append(name)
            continue
        # If min_days was specified, drop any instruments that don't meet the criteria.
        # We need to do this is a separate loop so the trimmed end date is available.
        if min_days is not None and ret.count() < min_days:
            emsg = "Excluding returns column: {} as it doesn't have {} consecutive days of returns, only ({})."
            logger.warn(emsg.format(name, min_days, ret.count()))
            to_drop.append(name)
        if latest_start is not None and ret.first_valid_index().date() > latest_start:
            emsg = "Excluding returns column: {} as it's first valid date: {} is after latest_start: {}."
            logger.warn(emsg.format(name, ret.first_valid_index().date(), latest_start))
            to_drop.append(name)

    return returns.drop(to_drop, axis=1)


def get_benchmark_returns(funds, benchmark_returns):
    """
    Simply returns the fund returns based on the benchmark returns
    :param funds: Iterable of Ticker items.
    :param benchmark_returns: Returns for benchmarks in the system.
    :return: A pandas timeseries dataframe with a column labels of the fund ids, with benchmark return values.
    """
    returns = pd.DataFrame()
    for fund in funds:
        if fund.benchmark is None:
            emsg = "Excluding fund: {} that has no benchmark defined."
            logger.warn(emsg.format(fund))
            continue
        bid = benchmark_uid(fund)
        if bid not in benchmark_returns:
            emsg = "Excluding fund: {} as its benchmark has no returns available."
            logger.warn(emsg.format(fund))
            continue
        returns[fund.id] = benchmark_returns[bid]
    return returns


def get_return_history(funds, start_date, end_date):
    """
    Returns the longest daily return history of the funds and their benchmarks for the given date range.
    The history may have gaps.

    :param funds: The iterable of funds (Tickers) we want the data for.
    :param start_date: The first date inclusive.
    :param end_date: The last date inclusive.
    :return: (fund_returns, benchmark_returns)
            - fund_returns is a pandas time series dataframe with one column per fund, column names are Ticker ids
            - benchmark_returns is a pandas time series dataframe with one column per benchmark.
              column names are "benchmark_content_type_id"_"benchmark_model_instance_id"
    """
    # TODO: Add asset class returns to this as well
    benchmark_returns = pd.DataFrame()
    fund_returns = pd.DataFrame()

    dates = pd.bdate_range(start_date, end_date)

    for fund in funds:
        # Add the benchmark returns if they're not already in there
        # We need to use the content type to disambiguate the object Id as the same id may be used in multiple models.
        fund_returns[fund.id] = fund.get_returns(dates)
        if fund.benchmark is None:
            emsg = "Fund: {} has no benchmark defined."
            logger.warn(emsg.format(fund))
            continue
        bid = benchmark_uid(fund)
        if bid not in benchmark_returns:
            benchmark_returns[bid] = fund.benchmark.get_returns(dates)

    return fund_returns, benchmark_returns


def get_fund_returns__OLD(funds, start_date, end_date, end_tol=0, min_days=None):
    """
    Returns the daily returns of the funds, and their benchmarks for the given date range.

    Results will be a consecutive time block of returns, all ending on the same day.
    The date they end on must be within 'end_tol' of the specified ending day.
    NaNs may exist at the start of some funds or benchmarks if data was not available for them.

    :param funds: The iterable of funds (Tickers) we want the data for.
    :param start_date: The first date inclusive.
    :param end_date: The last date inclusive.
    :param end_tol: The maximum number of days before end_date the series is allowed to end.
    :param min_days: The minimum number of days that need to be available for a fund to be included.
    :return: (fund_returns, benchmark_returns, mappings)
            - fund_returns is a Pandas DataFrame of return series for each fund. Column names are their ticker ids.
            - benchmark_returns is a Pandas DataFrame of return series for each benchmark.
              Column names are their content_type ids.
            - mappings is a dict from ticker ids to content_type ids, so we know which goes with which.
    """
    min_end = end_date - timedelta(days=end_tol)
    fund_returns = pd.DataFrame()
    benchmark_returns = pd.DataFrame()
    mappings = {}  # Map from fund to benchmark
    max_end = end_date


    # Map from benchmark to list of funds using it
    b_to_f = defaultdict(list)
    dates = pd.bdate_range(start_date, end_date)

    for fund in funds:
        ser = fund.get_returns(dates)
        last_dt = ser.last_valid_index()
        if last_dt is None:
            emsg = "Excluding fund: {} as it has no returns available."
            logger.warn(emsg.format(fund))
            continue
        last_dt = last_dt.date()  # convert to datetime
        last_dt = datetime(last_dt.year, last_dt.month, last_dt.day)
        if fund.benchmark is None:
            emsg = "Excluding fund: {} as it has no benchmark defined."
            logger.warn(emsg.format(fund))
            continue

        # Add the benchmark returns if they're not already in there
        # We need to use the content type to disambiguate the object Id as the same id may be used in multiple models.
        bid = benchmark_uid(fund)
        brets = None
        if bid not in benchmark_returns:
            brets = fund.benchmark.get_returns(dates)
            blast_dt = brets.last_valid_index()
            if blast_dt is None:
                emsg = "Excluding fund: {} as its benchmark: {} has no returns available."
                logger.warn(emsg.format(fund, fund.benchmark))
                continue
            blast_dt = blast_dt.date()  # convert to datetime
            blast_dt = datetime(blast_dt.year, blast_dt.month, blast_dt.day)
            last_dt = min(blast_dt, last_dt)
            if blast_dt < min_end:
                emsg = "Excluding fund: {} as the last day of data for its benchmark is before {} (the minimum acceptable)."
                logger.warn(emsg.format(fund, blast_dt))
                continue

        if last_dt < min_end:
            emsg = "Excluding fund: {} as it's last day of data is before {} (the minimum acceptable)."
            logger.warn(emsg.format(fund, last_dt))
            continue
        max_end = min(max_end, last_dt)
        fund_returns[fund.id] = ser
        b_to_f[bid].append(fund.id)
        mappings[fund.id] = bid
        if brets is not None:
            benchmark_returns[bid] = brets

    if max_end != end_date:
        fund_returns = fund_returns.iloc[:fund_returns.index.get_loc(max_end)+1]
        benchmark_returns = benchmark_returns.iloc[:benchmark_returns.index.get_loc(max_end)+1]

    # If min_days was specified, drop any instruments that don't meet the criteria.
    # We need to do this is a separate loop so the trimmed end date is available.
    if min_days is not None:
        to_drop = []
        for iid, ser in fund_returns.iteritems():
            if ser.count() < min_days:
                emsg = "Excluding fund: {} as it doesn't have {} consecutive days of returns ending on {}."
                logger.warn(emsg.format(iid, min_days, max_end))
                to_drop.append(iid)
                bid = mappings[iid]
                b_to_f[bid].remove(iid)  # Remove the fund from the reverse mapping
                if len(b_to_f[bid]) == 0:
                    del b_to_f[bid]
                    benchmark_returns.drop(bid, axis=1, inplace=1)
                del mappings[iid]  # Remove the fund from the mappings
        fund_returns.drop(to_drop, axis=1, inplace=1)

        # Also check each of the benchmarks has enough data
        to_drop = []
        for bid, ser in benchmark_returns.iteritems():
            if ser.count() < min_days:
                emsg = "Excluding benchmark: {} and all it's funds as it doesn't have {} consecutive days of returns ending on {}."
                logger.warn(emsg.format(bid, min_days, max_end))
                to_drop.append(bid)
                for fid in b_to_f[bid]:
                    logger.warn("Removing fund: {}".format(fid))
                    del mappings[fid]
                    fund_returns.drop(fid, axis=1, inplace=1)
                del b_to_f[bid]
        benchmark_returns.drop(to_drop, axis=1, inplace=1)

    return fund_returns, benchmark_returns, mappings


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

    # to_timeseries only works with django-pandas from QuerySet.
    # We might be sending DataFrame already with different data_provider
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


def get_price_returns(instrument, dates, consecutive=False):
    """
    Get the daily returns series for the given instrument.
    The data should be clean from outliers, but may have gaps.
    :param instrument:
    :param dates: Pandas datetime index of dates to collect.
    :param consecutive: Only return the latest consecutive run of returns.
    :return:
    """
    prices = get_prices(instrument, dates)
    consec = prices[prices.first_valid_index():prices.last_valid_index()].astype(float)
    if consecutive:
        consec = consec[first_consec_index(consec):]

    if consec.count() != consec.size:
        emsg = "Not generating full returns for instrument: {}. " \
               "Generating longest data available from {} - {}"
        logger.warn(emsg.format(instrument.id, consec.index[0], consec.index[-1]))

    # Convert the prices to log returns
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
