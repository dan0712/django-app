import datetime
import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Max
from django.core.management.base import BaseCommand

from main.models import DailyPrice, Ticker

logger = logging.getLogger("set_prices")


def populate_current_prices():
    m1w = (datetime.datetime.today() - datetime.timedelta(days=7)).date()

    # Set the unit price to the latest we have in the DB.
    for price in DailyPrice.objects.exclude(price__isnull=True).values('instrument_content_type_id',
                                                                       'instrument_object_id').annotate(last=Max('date')):
        instrument_ct = ContentType.objects.get_for_id(price['instrument_content_type_id'])
        instrument = instrument_ct.get_object_for_this_type(id=price['instrument_object_id'])
        if hasattr(instrument, 'unit_price'):
            dt = price['last']
            if dt < m1w:
                emsg = "The most current price for '{}' is more than one week old ({})." \
                       " Consider running the 'load_prices' command."
                logger.warn(emsg.format(instrument.display_name, dt))
            instrument.unit_price = DailyPrice.objects.get(instrument_content_type_id=price['instrument_content_type_id'],
                                                           instrument_object_id=price['instrument_object_id'],
                                                           date=dt).price
            instrument.save()


class Command(BaseCommand):
    help = 'Populates the unit prices stored on the instruments from the DailyPrice data.'

    def handle(self, *args, **options):
        populate_current_prices()
