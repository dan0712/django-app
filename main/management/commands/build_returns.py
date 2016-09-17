import logging
from datetime import datetime

import pandas as pd

from django.core.management.base import BaseCommand

from portfolios.returns import build_returns


logger = logging.getLogger("build_returns")


def parse_date(val):
    return datetime.strptime(val, '%Y%m%d').date()


class Command(BaseCommand):
    help = 'Populates Return tables for the given dates.'

    def add_arguments(self, parser):
        parser.add_argument('begin_date', type=parse_date, help='Inclusive start date to load the data for. (YYYYMMDD)')
        parser.add_argument('end_date', type=parse_date, help='Inclusive end date to load the data for. (YYYYMMDD)')

    def handle(self, *args, **options):
        dates = pd.bdate_range(options['begin_date'], options['end_date'])
        build_returns(dates)
