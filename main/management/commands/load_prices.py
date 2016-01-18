from collections import defaultdict
import datetime
import logging
import math

from django.core.management.base import BaseCommand
from django.db.models.aggregates import Max

from main.models import Ticker, DailyPrice, MonthlyPrices, ExchangeRate
from portfolios.api.bloomberg import get_fund_hist_data as bl_getter, get_fx_rates
from portfolios.models import MarketCap

logger = logging.getLogger("load_prices")

api_map = {'portfolios.api.bloomberg': bl_getter}

# TODO: Make the system currency a setting for the site
SYSTEM_CURRENCY = 'AUD'

# Module level cache of currency data.
currency_cache = {}


def load_fx_rates(begin_date, end_date):
    # Get the currencies of interest
    currs = []
    seconds = []
    coi = Ticker.objects.values_list('currency', flat=True).distinct()
    for curr in coi:
        if curr == SYSTEM_CURRENCY or curr in seconds:
            continue
        currs.append((SYSTEM_CURRENCY, curr))
        seconds.append(curr)

    # Get the new rates
    rates_frame = get_fx_rates(currs, begin_date, end_date)

    # Delete any existing rates for the date range and the currencies of interest
    ExchangeRate.objects.filter(
            date__range=(begin_date, end_date)).filter(
            first=SYSTEM_CURRENCY).filter(
            second__in=seconds).delete()

    # Insert the new monthly prices
    rates = []
    for row in rates_frame.itertuples():
        for ix, curr in enumerate(seconds):
            rates.append(ExchangeRate(first=SYSTEM_CURRENCY, second=curr, date=row[0], rate=row[ix + 1]))
    ExchangeRate.objects.bulk_create(rates)


def fx_convert(val, date, currency):
    if currency == SYSTEM_CURRENCY:
        return val
    rate = currency_cache.get((currency, date), None)
    if rate is None:
        rate = ExchangeRate.objects.filter(first=SYSTEM_CURRENCY,
                                           second=currency,
                                           date=date).values_list('rate', flat=True)
        if len(rate) == 0:
            msg = "Cannot convert currency: {} for date: {} as I don't have the exchange rate. maybe run load_fx_rates?"
            raise Exception(msg.format(currency, date))
        rate = rate[0]

    return val / rate


def nan_none(val):
    return None if math.isnan(val) else val


def load_ticker_data(begin_date, end_date):
    """

    :param begin_date:
    :param end_date:
    :return:
    """
    # Get the api details for all our tickers
    api_calls = defaultdict(list)
    id_map = {}
    for ticker in Ticker.objects.all():
        if ticker.data_api is None:
            logger.debug('Ignoring ticker: {} for data load as api not specified.'.format(ticker.pk))
            continue
        if ticker.data_api_param is None or not ticker.data_api_param.strip():
            logger.debug('Ignoring ticker: {} for data load as api param not specified.'.format(ticker.pk))
            continue

        # On second thoughts, lets not do this as it's a pretty good attack vector.
        # Instead, load the ones we know in the header
        # __import__(ticker.data_api)

        api_calls[ticker.data_api].append(ticker.data_api_param)
        id_map[ticker.data_api_param] = ticker

    # A list of (navseries, ticker) pairs.
    monthly_navs = []

    # Get the daily data from each api for the provided dates
    for api, ticker_params in api_calls.items():
        dframes = api_map[api](ticker_params, begin_date, end_date)

        # Load data into the django daily model, removing whatever's there
        for key, frame in dframes.items():
            ticker = id_map[key]

            # Generate the monthly prices from the frame.
            # We were throwing a segfault here on empty frame, so we don't do it now.
            if frame['nav'].size > 0:
                monthly_navs.append((frame['nav'].resample('M', how='last', closed='right', label='right'), ticker))
            else:
                emsg = "Not generating prices for symbol: {} as there is no data to use."
                logger.warn(emsg.format(ticker.symbol))

            # Delete any existing prices for the date range
            DailyPrice.objects.filter(ticker=ticker).filter(date__range=(begin_date, end_date)).delete()

            # Insert the new prices
            prices = [DailyPrice(ticker=ticker,
                                 date=dt,
                                 nav=nan_none(fx_convert(nav, dt, ticker.currency)),
                                 aum=nan_none(fx_convert(aum, dt, ticker.currency))) for dt, nav, aum in
                      frame.itertuples()]
            DailyPrice.objects.bulk_create(prices)

    # Load the MonthlyPrices table from the daily prices
    # First delete any existing prices for the date range
    # Pull the end_date back to the last end of month in the range.
    if (end_date + datetime.timedelta(days=1)).month == end_date.month:
        end_date = datetime.date(end_date.year, end_date.month, 1) - datetime.timedelta(days=1)

    if end_date < begin_date:
        msg = "Not setting monthly prices as no end of months covered in selected dates: {}-{}"
        logger.debug(msg.format(begin_date, end_date))
        return

    # Insert the new monthly prices
    monthly_prices = []
    for series, ticker in monthly_navs:
        MonthlyPrices.objects.filter(symbol=ticker.symbol).filter(date__range=(begin_date, end_date)).delete()
        monthly_prices += [MonthlyPrices(symbol=ticker.symbol,
                                         date=dt,
                                         price=fx_convert(price, dt, ticker.currency)) for dt, price in
                           series.iteritems() if dt <= datetime.datetime.combine(end_date, datetime.time())]
    MonthlyPrices.objects.bulk_create(monthly_prices)


def set_aum():
    """
    We generate the market cap from the date of the last monthly price we have available.
    """
    dates = {}
    for entry in MonthlyPrices.objects.values('symbol').annotate(last=Max('date')):
        dates[entry['symbol']] = entry['last']

    for mc in MarketCap.objects.all():
        date = dates.pop(mc.ticker.symbol, None)
        aum = get_aum(mc.ticker, date)
        if aum is None:
            logger.warn('No aum found for symbol: {}. Deleting old AUM'.format(mc.ticker.symbol))
            mc.delete()
            continue
        mc.value = aum
        mc.save()
        logger.debug("Set AUM entry for symbol: {}".format(mc.ticker.symbol))

    for sym, date in dates.items():
        ticker = Ticker.objects.filter(symbol=sym).first()
        if ticker is None:
            emsg = "Found monthly prices for symbol: {}, but there is no corresponding ticker. " \
                   "Please remove the monthly prices for that symbol"
            logger.warn(emsg.format(sym))
            continue
        aum = get_aum(ticker, date)
        if aum is not None:
            MarketCap.objects.create(ticker=ticker, value=aum)
            logger.debug("Inserted AUM entry for ticker: {}".format(ticker.pk))


def get_aum(ticker, date):
    aum = DailyPrice.objects.filter(ticker=ticker, date=date).values_list('aum', flat=True)
    if len(aum) == 0:
        dp = DailyPrice.objects.filter(ticker=ticker).exclude(aum__isnull=True).order_by('-date').first()
        if dp is None:
            emsg = 'No daily price containing AUM found for symbol: {}. Cannot set AUM.'
            logger.warn(emsg.format(ticker.symbol))
            return None
        emsg = 'No daily price found from last monthly price date: {} for symbol: {}. Using last AUM available from: {}'
        logger.warn(emsg.format(date, ticker.symbol, dp.date))
        return dp.aum
    else:
        return aum[0]


def parse_date(val):
    return datetime.datetime.strptime(val, '%Y%m%d').date()


class Command(BaseCommand):
    help = 'Loads exchange rates and ticker data from bloomberg for the given date range.'

    def add_arguments(self, parser):
        parser.add_argument('begin_date', type=parse_date, help='Inclusive start date to load the data for. (YYYYMMDD)')
        parser.add_argument('end_date', type=parse_date, help='Inclusive end date to load the data for. (YYYYMMDD)')

    def handle(self, *args, **options):
        load_fx_rates(options['begin_date'], options['end_date'])
        load_ticker_data(options['begin_date'], options['end_date'])
        set_aum()
