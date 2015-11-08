from django.core.management.base import BaseCommand, CommandError
from ...models import PortfolioSet, PortfolioByRisk
from main.models import Platform
from portfolios.api.yahoo import YahooApi, DbApi
from pandas import concat, ordered_merge, DataFrame
from portfolios.bl_model import handle_data, assets_covariance, calculate_co_vars
import json
import numpy as np


def get_api(api_name):
    api_dict = {"YAHOO": YahooApi()}
    return api_dict[api_name]


def calculate_portfolios(portfolio_set):
    api = DbApi()# get_api(Platform.objects.first().api)
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
    old_columns = list(table)
    new_assets_type = []
    views_dict = []
    qs = []

    tau = portfolio_set.tau
    constrains = []

    def create_constrain(_super_classes, _custom_size):
        def evaluate(_columns, x):
            _super_class_array = np.array([])
            for _c in _columns:
                if _c in _super_classes:
                    _super_class_array = np.append(_super_class_array, [1])
                else:
                    _super_class_array = np.append(_super_class_array, [0])
            jac = 2*(sum(x*_super_class_array) - _custom_size)*np.array(_super_class_array)
            func = (sum(x*_super_class_array) - _custom_size)**2  
            return func, jac
        return evaluate

    only_use_this_assets = []
    au_size = 0.5
    super_classes = []
    for ticker_idx in range(0, len(old_columns)):
        if asset_super_class_dict[old_columns[ticker_idx]]:
            super_classes.append(old_columns[ticker_idx])
            only_use_this_assets.append(old_columns[ticker_idx])
    constrains.append(create_constrain(super_classes, au_size))
    
    dm_size = 0.5
    super_classes = []
    for ticker_idx in range(0, len(old_columns)):
        if dm_asset_super_class_dict[old_columns[ticker_idx]]:
            super_classes.append(old_columns[ticker_idx])
            only_use_this_assets.append(old_columns[ticker_idx])
    constrains.append(create_constrain(super_classes, dm_size))

    table = table.reindex(index=None, columns=only_use_this_assets)
    columns = list(table)

    # get views
    for view in portfolio_set.views.all():
        _append = True
        new_view_dict = {}
        header, view_values = view.assets.splitlines()

        header = header.split(",")
        view_values = view_values.split(",")

        for i in range(0, len(header)):
            _symbol = header[i].strip()
            if _symbol not in columns:
                _append = False

            new_view_dict[header[i].strip()] = float(view_values[i])

        if not _append:
            continue
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

    # delete all the risk profiles related to this portfolio set
    portfolio_set.risk_profiles.all().delete()
    tm = 0
    mw = np.array([])
    # calculate total market cap
    # create market w
    for ticker_idx in range(0, len(columns)):
        mw = np.append(mw, market_cap[columns[ticker_idx]])
        tm += market_cap[columns[ticker_idx]]

    if tm == 0:
        mw = np.ones([len(mw)])/len(mw)
    else:
        mw = mw/tm
    
    initial_w = mw

    assets_len = len(columns)
    expected_returns = np.array([])
    # Drop missing values and transpose matrix

    # calculate expected returns
    for i in range(assets_len):
        er = (1+np.mean(table[columns[i]].pct_change()))**12 - 1
        expected_returns = np.append(expected_returns, er)
    # calculate covariance matrix
    sk_co_var, co_vars = calculate_co_vars(assets_len, table)

    for allocation in list(np.around(np.arange(0, 1.01, 0.01), decimals=2)):
        # calculate optimal portfolio for different risks 0 - 100
        new_weights, _mean, var = handle_data(assets_len, expected_returns, sk_co_var, co_vars,
                                              portfolio_set.risk_free_rate, allocation,
                                              new_assets_type,  views, qs, tau, constrains, mw,
                                              initial_w, columns)

        _mean = float("{0:.4f}".format(_mean))*100
        var = float("{0:.4f}".format((var*100*100)**(1/2)))
        allocations = {}

        for column in old_columns:
            if column in columns:
                idx = columns.index(column)
                allocations[ticker_parent_dict[column]] = float("{0:.4f}".format(new_weights[idx]))
            else:
                allocations[ticker_parent_dict[column]] = 0
      
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
