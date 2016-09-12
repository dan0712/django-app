from django.core.management.base import BaseCommand

from main.models import Goal


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        for goal in Goal.objects.all():
            goal.portfolios = None
            goal.save()
