import logging

from django.core.management.base import BaseCommand

from main.models import Goal
from portfolios.calculation import Unsatisfiable, \
    calculate_portfolios
from portfolios.providers.data.django import DataProviderDjango
from portfolios.providers.execution.django import ExecutionProviderDjango

logger = logging.getLogger('betasmartz.portfolio_calculation')



class Command(BaseCommand):
    help = 'Calculate all the optimal portfolios for all the goals in the system.'

    def handle(self, *args, **options):
        # calculate portfolios
        data_provider = DataProviderDjango()
        exec_provider = ExecutionProviderDjango()
        for goal in Goal.objects.all():
            if goal.selected_settings is not None:
                try:
                    calculate_portfolios(setting=goal.selected_settings,
                                         data_provider=data_provider,
                                         execution_provider=exec_provider)
                except Unsatisfiable as e:
                    logger.warn(e)
