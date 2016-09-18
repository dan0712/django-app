from django.core.management.base import BaseCommand

from main.models import Ticker


def populate_features():
    """
    Converts the old constraint version to the new, and saves them in the db.
    :return: Nothing
    """

    # Populate the features for instruments from old features #
    for ticker in Ticker.objects.all():
        print('Populating features for ticker %s' % ticker)
        ticker.save()  # populate_features should call off post_save


class Command(BaseCommand):
    help = 'Populate asset features for all assets in the system.'

    def handle(self, *args, **options):
        populate_features()
