__author__ = 'cristian'

from django.core.management.base import BaseCommand
from main.models import Goal


def remove_old_custom_portfolios():
    for goal in Goal.objects.all():
        goal.portfolios = None
        goal.save()


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        remove_old_custom_portfolios()
