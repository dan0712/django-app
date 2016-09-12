from django.core.cache import cache
from main import redis
from django.utils.timezone import now
from portfolios.management.commands.portfolio_calculation_pure import \
    build_instruments, Unsatisfiable, calculate_portfolios
from portfolios.management.commands.providers.instruments_data_providers.data_provider_django import DataProviderDjango
from django.core.management.base import BaseCommand
from main.models import Goal
import logging

logger = logging.getLogger('betasmartz.portfolio_calculation')
#logger.setLevel(logging.INFO)


def get_instruments(data_provider=None):
    '''
    :param data_provider: data provider to query data when results are not cached
    :return:
    '''
    key = redis.KEY_INSTRUMENTS(now().today().isoformat())
    data = cache.get(key)

    if data is None:
        data = build_instruments(data_provider=data_provider)
        cache.set(key, data, timeout=60 * 60 * 24)

    return data


def get_all_optimal_portfolios():
    # calculate portfolios
    data_provider = DataProviderDjango()
    for goal in Goal.objects.all():
        if goal.selected_settings is not None:
            try:
                calculate_portfolios(setting=goal.selected_settings, data_provider=data_provider)
            except Unsatisfiable as e:
                logger.warn(e)


class Command(BaseCommand):
    help = 'Calculate all the optimal portfolios for all the goals in the system.'

    def handle(self, *args, **options):
        logger.setLevel(logging.DEBUG)
        get_all_optimal_portfolios()
