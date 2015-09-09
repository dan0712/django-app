from django.core.management.base import BaseCommand, CommandError
from ...models import PortfolioSet


def calculate_portfolios(portfolio_set):
    print(portfolio_set)
    pass


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        for ps in PortfolioSet.objects.all():
            calculate_portfolios(ps)