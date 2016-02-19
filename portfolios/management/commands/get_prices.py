import datetime
import logging

from django.db.models.aggregates import Max
from django.core.management.base import BaseCommand

from main.models import Goal, DailyPrice, Ticker

logger = logging.getLogger("get_prices")


def populate_current_prices():
    m1w = (datetime.datetime.today() - datetime.timedelta(days=7)).date()

    # Set the unit price to the latest we have in the DB.
    for price in DailyPrice.objects.exclude(nav__isnull=True).values('ticker').annotate(last=Max('date')):
        ticker = Ticker.objects.get(pk=price['ticker'])
        dt = price['last']
        if dt < m1w:
            emsg = "The most current NAV for symbol: {} in asset class: {} " \
                   "is more than one week old ({}). Consider running the 'load_prices' command."
            logger.warn(emsg.format(ticker.symbol, ticker.asset_class.name, dt))
        ticker.unit_price = DailyPrice.objects.get(ticker=ticker, date=dt).nav
        ticker.save()

    # Set the calculated values on the goals using the new ticker navs.
    '''
    for goal in Goal.objects.all():
        goal.drift = goal.get_drift
        goal.total_balance_db = goal.total_balance
        goal.save()
    '''


class Command(BaseCommand):
    help = 'Populates the unit prices stored on the tickers, then updates the drift and balance on the goals.'

    def handle(self, *args, **options):
        populate_current_prices()
