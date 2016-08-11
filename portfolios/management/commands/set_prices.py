import logging
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Max
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from main.models import DailyPrice, Ticker

logger = logging.getLogger("set_prices")


def populate_current_prices():
    m1w = (now().today() - timedelta(days=7)).date()

    # Set the unit price to the latest we have in the DB.
    for price in DailyPrice.objects.exclude(price__isnull=True).values('instrument_content_type_id',
                                                                       'instrument_object_id').annotate(last=Max('date')):
        instrument_ct = ContentType.objects.get_for_id(price['instrument_content_type_id'])
        try:
            instrument = instrument_ct.get_object_for_this_type(id=price['instrument_object_id'])
            logger.info('Found instrument with object id %s' % price['instrument_object_id'])
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
        except ObjectDoesNotExist:
            # not found? why? log it - current dev dataset does not have tickers
            # with matching id's for some of the ids returned
            logger.error('ObjectDoesNotExist for instrument with object id %s' % price['instrument_object_id'])
            pass


class Command(BaseCommand):
    help = 'Populates the unit prices stored on the instruments from the DailyPrice data.'

    def handle(self, *args, **options):
        populate_current_prices()
