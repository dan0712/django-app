from django.core.management.base import BaseCommand, CommandError
from ...models import PortfolioSet, PortfolioByRisk
from main.models import Platform
from portfolios.api.yahoo import YahooApi, DbApi
from pandas import concat, ordered_merge, DataFrame
from portfolios.bl_model import handle_data
import json
import numpy as np


def get_api(api_name):
    api_dict = {"YAHOO": YahooApi()}
    return api_dict[api_name]


def calculate_portfolios(portfolio_set):
    api = DbApi()#get_api(Platform.objects.first().api)
    # get all the assets
    series = {}
    asset_type = {}
    asset_name = []
    asset_super_class_dict = {}
    dm_asset_super_class_dict = {}
    market_cap = dict()
    ticker_parent_dict = {}
    for asset in portfolio_set.asset_classes.all():
        ticker = asset.tickers.filter(ordering=0).first()
        asset_name.append(ticker.symbol)
        asset_super_class_dict[ticker.symbol] = 1 if asset.super_asset_class in ["EQUITY_AU", "FIXED_INCOME_AU"] else 0
        dm_asset_super_class_dict[ticker.symbol] = 1 if asset.super_asset_class in ["EQUITY_INT", "FIXED_INCOME_INT"] else 0
        series[ticker.symbol] = api.get_all_prices(ticker.symbol)
        ticker_parent_dict[ticker.symbol] = asset.name
        asset_type[ticker.symbol] = 0 if asset.investment_type == 'BONDS' else 1
        market_cap[ticker.symbol] = api.market_cap(ticker)

    # join all the series in a table, drop missing values
    table = DataFrame(series)
    new_assets_type = []
    views_dict = []
    qs = []

    tau = portfolio_set.tau
    for view in portfolio_set.views.all():
        new_view_dict = {}
        header, view_values = view.assets.splitlines()

        header = header.split(",")
        view_values = view_values.split(",")

        for i in range(0, len(header)):
            new_view_dict[header[i].strip()] = float(view_values[i])
        views_dict.append(new_view_dict)
        qs.append(view.q)

    views = []
    for vd in views_dict:
        new_view = []
        for c in list(table):
            new_view.append(vd.get(c, 0))
        views.append(new_view)

    for c in list(table):
        new_assets_type.append(asset_type[c])

    columns = list(table)

    constrains = []

    def create_constrain(_super_class_array, _custom_size):
        def evaluate(x):
            jac = 2*(sum(x*_super_class_array) - _custom_size)*np.array(_super_class_array)
            func = (sum(x*_super_class_array) - _custom_size)**2  
            return func, jac
        return evaluate

    au_size = 0.5
    super_class_array = np.zeros((len(columns)))
    for ticker_idx in range(0, len(columns)):
        super_class_array[ticker_idx] = asset_super_class_dict[columns[ticker_idx]]
    constrains.append(create_constrain(super_class_array, au_size))
    
    dm_size = 0.5
    super_class_array = np.zeros((len(columns)))
    for ticker_idx in range(0, len(columns)):
        super_class_array[ticker_idx] = dm_asset_super_class_dict[columns[ticker_idx]]
    constrains.append(create_constrain(super_class_array, dm_size))

    # delete all the risk profiles related to this portfolio set
    portfolio_set.risk_profiles.all().delete()
    tm = 0
    # calculate total market cap
    for k, v in market_cap.items():
        tm += v
  
    mw = []
    # create market w
    for ticker_idx in range(0, len(columns)):
        mw.append(market_cap[columns[ticker_idx]] / tm)
    
    initial_w = mw
    for allocation in list(np.arange(0, 1.01, 0.01)):
        # calculate optimal portfolio for different risks 0 - 100
        new_weights, _mean, var = handle_data(table, portfolio_set.risk_free_rate, allocation,
                                              new_assets_type,  views, qs, tau, constrains, mw, initial_w)

        _mean = float("{0:.4f}".format(_mean))*100
        var = float("{0:.4f}".format((var*100*100)**(1/2)))
        allocations = {}

        for idx in range(0, len(columns)):
            allocations[ticker_parent_dict[columns[idx]]] = float("{0:.4f}".format(new_weights[idx]))
      
        initial_w = new_weights
        allocations = json.dumps(allocations)
        pf = PortfolioByRisk(portfolio_set=portfolio_set, risk=allocation, expected_return=_mean,
                             volatility=var, allocations=allocations)
        pf.save()


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        for ps in PortfolioSet.objects.all():
            calculate_portfolios(ps)
