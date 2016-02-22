from django.core.management.base import BaseCommand, CommandError
from main.models import Platform, Performer, Ticker, SymbolReturnHistory, PERFORMER_GROUP_STRATEGY, PortfolioSet
from portfolios.api.yahoo import YahooApi
from pandas import concat, ordered_merge, DataFrame
import json
import numpy as np


def get_api(api_name):
    api_dict = {"YAHOO": YahooApi()}
    return api_dict[api_name]


def get_historical_returns():
    api = get_api(Platform.objects.first().api)
    symbols = []
    # get all the symbols
    for p in Performer.objects.all():
        if p.group == PERFORMER_GROUP_STRATEGY:
            continue
        if p.symbol:
            symbols.append(p.symbol)

    for t in Ticker.objects.all():
        symbols.append(t.symbol)

    symbols = set(symbols)
    series = {}

    for symbol in symbols:
        series[symbol] = api.get_all_prices(symbol, period='d')

    # join all the series in a table, drop missing values

    table = DataFrame(series)
    # get returns drop missing values
    returns = table.pct_change().dropna()
    returns_t = returns.values

    # save

    for i in list(returns):
        idx = 0
        for k in returns.index.tolist():
            s, is_new = SymbolReturnHistory.objects.get_or_create(symbol=i, date=k)
            s.return_number = returns[i][idx]
            s.save()
            idx += 1

    # save strategies
    for p in Performer.objects.filter(group=PERFORMER_GROUP_STRATEGY).all():
        allocation = float("{:.2f}".format(p.allocation))
        p.symbol = "ALLOC{0}".format(allocation)
        p.save()
        # get target portfolio

        portfolio_set = p.portfolio_set
        portfolios = json.loads(portfolio_set.portfolios)
        target_allocation_dict = portfolios["{:.2f}".format(allocation)]

        target_allocation = []
        for c_symbol in list(returns):
            fraction = 0
            # check if symbol is the ticker db
            tickers = Ticker.objects.filter(symbol=c_symbol).all()
            if tickers:
                ticker = tickers[0]
                if ticker.ordering == 0:
                    asset = ticker.asset_class.name
                    fraction = target_allocation_dict.get(asset, 0)
            target_allocation.append(fraction)

        target_allocation = np.array(target_allocation)
        strategy_returns = np.dot(returns_t, target_allocation)
        idx = 0
        for k in returns.index.tolist():
            s, is_new = SymbolReturnHistory.objects.get_or_create(symbol=p.symbol, date=k)
            s.return_number = strategy_returns[idx]
            s.save()
            idx += 1


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        get_historical_returns()