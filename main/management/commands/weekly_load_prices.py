import logging
from main.management.commands.load_prices import load_fx_rates, load_price_data
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

logger = logging.getLogger("weekly_load_prices")


class Command(BaseCommand):
    help = 'Loads exchange rates and ticker data from bloomberg from a week ago to today.'

    def handle(self, *args, **options):
        # this runs load_prices from a week ago to today
        end_date = datetime.date(datetime.now())
        begin_date = end_date - timedelta(days=7)
        load_fx_rates(begin_date, end_date)
        load_price_data(begin_date, end_date)
