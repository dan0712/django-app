from django.core.management.base import BaseCommand, CommandError
from ...models import PortfolioSet, PortfolioByRisk
from main.models import Platform, Performer, Ticker, SymbolReturnHistory, STRATEGY, Goal, Transaction, MARKET_CHANGE, EXECUTED
from portfolios.api.yahoo import YahooApi
from pandas import concat, ordered_merge, DataFrame
from portfolios.bl_model import handle_data
import json
import numpy as np


def get_api(api_name):
    api_dict = {"YAHOO": YahooApi()}
    return api_dict[api_name]


def demo_accounts_returns():
    api = get_api(Platform.objects.first().api)
    symbols = []

    # get all the symbols
    for t in Ticker.objects.all():
        symbols.append(t.symbol)

    symbols = symbols
    series = {}

    for symbol in symbols:
        series[symbol] = api.get_all_prices(symbol, period='d')

    # join all the series in a table, drop missing values

    table = DataFrame(series).dropna()
    # drop missing values
    returns = table.values

    # save strategies
    for goal in Goal.objects.all():
        positions_dict = {}
        # get positions
        for pos in goal.positions.all():
            positions_dict[pos.ticker.symbol] = pos.share

        positions = []
        for c_symbol in list(table):
            # check if symbol is the ticker db
            shares = positions_dict.get(c_symbol, 0)
            positions.append(shares)

        positions = np.array(positions)
        goal_values = np.dot(returns, positions)
        inv = goal_values[0]
        if inv == 0:
            continue

        counter = 0
        for k in table.index.tolist()[1:]:
            counter += 1
            transaction, is_new = Transaction.objects.get_or_create(type=MARKET_CHANGE, created_date=k, account=goal)
            transaction.inversion = inv
            transaction.amount = goal_values[counter] - goal_values[counter-1]
            transaction.status = EXECUTED
            transaction.executed_date = k
            transaction.return_fraction = (goal_values[counter] - goal_values[counter-1])/goal_values[counter-1]
            transaction.new_balance = goal_values[counter]
            transaction.save()


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        demo_accounts_returns()