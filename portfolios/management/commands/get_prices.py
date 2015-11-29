__author__ = 'cristian'

from django.core.management.base import BaseCommand, CommandError
from ...models import PortfolioSet
from main.models import Platform, Goal
from portfolios.api.yahoo import YahooApi
from pandas import concat, ordered_merge, DataFrame
from portfolios.bl_model import handle_data
import json
import numpy as np


def get_api(api_name):
    api_dict = {"YAHOO": YahooApi()}
    return api_dict[api_name]


def calculate_prices(portfolio_set):
    api = get_api(Platform.objects.first().api)
    # get all the assets
    for asset in portfolio_set.asset_classes.all():
        ticker = asset.tickers.filter(ordering=0).first()
        unit_price = api.get_unit_price(ticker.symbol, ticker.currency)
        if unit_price is not None:
            ticker.unit_price = unit_price
            ticker.save()

    for goal in Goal.objects.all():
        goal.drift = goal.get_drift
        goal.total_balance_db = goal.total_balance
        goal.save()


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        for ps in PortfolioSet.objects.all():
            calculate_prices(ps)