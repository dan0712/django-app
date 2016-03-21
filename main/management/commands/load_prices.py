from collections import defaultdict
import datetime
import logging
import math

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from main.models import Ticker, MarketIndex, DailyPrice, ExchangeRate, SYSTEM_CURRENCY
from portfolios.api.bloomberg import get_fund_hist_data as bl_getter, get_fx_rates

logger = logging.getLogger("load_prices")

api_map = {'portfolios.api.bloomberg': bl_getter}

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

    def make_weekday(date):
        if date.weekday() > 4:
            new_date = date - datetime.timedelta(days=date.weekday() - 4)
            msg = "Not attempting currency conversion for weekend day: {}. Trying previous workday: {}."
            logger.info(msg.format(date.date(), new_date.date()))
            date = new_date
        return date

    date = make_weekday(date)
    rate = currency_cache.get((currency, date), None)
    if rate is None:
        rate = ExchangeRate.objects.filter(first=SYSTEM_CURRENCY,
                                           second=currency,
                                           date=date).values_list('rate', flat=True)
        # if len(rate) == 0 or not rate[0] or not rate[0][0] or not math.isfinite(rate[0][0]):
        if len(rate) == 0 or not rate[0] or not math.isfinite(rate[0]):
            old_dt = date
            date = make_weekday(date - datetime.timedelta(days=1))
            msg = "Cannot convert currency: {} for date: {} as I don't have the exchange rate. Maybe run load_fx_rates?"
            msg2 = " Trying the previous workday: {}."
            logger.warn((msg + msg2).format(currency, old_dt.date(), date.date()))
            rate = ExchangeRate.objects.filter(first=SYSTEM_CURRENCY,
                                               second=currency,
                                               date=date).values_list('rate', flat=True)
            if len(rate) == 0 or not rate[0] or not math.isfinite(rate[0]):
                raise Exception(msg.format(currency, date))
        # print(rate[0])
        rate = rate[0]

    return val / rate


def nan_none(val):
    return None if math.isnan(val) else val


def load_price_data(begin_date, end_date):
    """

    :param begin_date:
    :param end_date:
    :return:
    """
    api_calls = defaultdict(list)
    id_map = {}

    # Get the api details for all our funds
    for fund in Ticker.objects.all():
        if fund.data_api is None:
            logger.debug('Ignoring fund: {} for data load as api not specified.'.format(fund.pk))
            continue
        if fund.data_api_param is None or not fund.data_api_param.strip():
            logger.debug('Ignoring fund: {} for data load as api param not specified.'.format(fund.pk))
            continue

        api_calls[fund.data_api].append(fund.data_api_param)
        id_map[fund.data_api_param] = fund

    # Get the api details for all our indices
    for index in MarketIndex.objects.all():
        if index.data_api is None:
            logger.debug('Ignoring index: {} for data load as api not specified.'.format(index.pk))
            continue
        if index.data_api_param is None or not index.data_api_param.strip():
            logger.debug('Ignoring index: {} for data load as api param not specified.'.format(index.pk))
            continue

        api_calls[index.data_api].append(index.data_api_param)
        id_map[index.data_api_param] = index

    # Get the daily data from each api for the provided dates
    for api, instr_params in api_calls.items():
        dframes = api_map[api](instr_params, begin_date, end_date)

        # Load data into the django daily model, removing whatever's there
        for key, frame in dframes.items():
            instr = id_map[key]

            # Delete any existing prices for the date range
            instr_type = ContentType.objects.get_for_model(instr)
            DailyPrice.objects.filter(instrument_content_type=instr_type,
                                      instrument_object_id=instr.id,
                                      date__range=(begin_date, end_date)).delete()

            # Insert the new prices
            prices = []
            for dt, price in frame.itertuples():
                prices.append(DailyPrice(instrument=instr,
                                         date=dt,
                                         price=fx_convert(price, dt, instr.currency)))
                # print("Appended {} from sym: {}, dt: {}, nav: {}".format(prices[-1].nav, key, dt, nav))

            DailyPrice.objects.bulk_create(prices)


'''
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
'''


def parse_date(val):
    return datetime.datetime.strptime(val, '%Y%m%d').date()


class Command(BaseCommand):
    help = 'Loads exchange rates and ticker data from bloomberg for the given date range.'

    def add_arguments(self, parser):
        parser.add_argument('begin_date', type=parse_date, help='Inclusive start date to load the data for. (YYYYMMDD)')
        parser.add_argument('end_date', type=parse_date, help='Inclusive end date to load the data for. (YYYYMMDD)')
        # parser.add_argument('--verbose', '-v', action='count', help='Increase logging verbosity')

    def handle(self, *args, **options):

        if options['verbosity'] == 0:
            logger.setLevel(min(logging.WARN, logger.level))
        elif options['verbosity'] == 1:
            logger.setLevel(min(logging.INFO, logger.level))
        elif options['verbosity'] >= 2:
            logger.setLevel(min(logging.DEBUG, logger.level))

        load_fx_rates(options['begin_date'], options['end_date'])
        load_price_data(options['begin_date'], options['end_date'])
        # set_aum()
