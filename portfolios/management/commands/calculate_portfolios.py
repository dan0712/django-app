import json

import numpy as np
from django.core.management.base import BaseCommand
from main.models import Goal, AssetClass
from pandas import DataFrame
from portfolios.api.yahoo import YahooApi, DbApi
from portfolios.bl_model import handle_data, calculate_co_vars
from ...models import PortfolioSet
from typing import List, Dict


def get_api(api_name):
    api_dict = {"YAHOO": YahooApi()}
    return api_dict[api_name]


def is_from_region(super_asset_class_of, _ticker: str, _region: str):
    return 1 if _region in super_asset_class_of[_ticker] else 0


def create_constrain(_super_classes, _custom_size: float):
    def evaluate(_columns, x):
        _super_class_array = np.array([])
        for _c in _columns:
            if _c in _super_classes:
                _super_class_array = np.append(_super_class_array, [1])
            else:
                _super_class_array = np.append(_super_class_array, [0])
        jac = 2 * (sum(x * _super_class_array) - _custom_size) * np.array(_super_class_array)
        func = (sum(x * _super_class_array) - _custom_size) ** 2
        return func, jac

    return evaluate


def calculate_portfolios_dual_region(goal: Goal, all_assets: List[AssetClass], portfolio_set: PortfolioSet,
                                     default_region: str, regions: Dict[str, dict], api=None):
    regions_with_bond_and_stock = dict()
    regions_with_only_bonds = dict()
    regions_with_only_stocks = dict()

    for k, v in regions.items():
        if v["has_bonds"] and v["has_stocks"]:
            regions_with_bond_and_stock[k] = v
        elif v["has_stocks"]:
            regions_with_only_stocks[k] = v
        else:
            regions_with_only_bonds[k] = v

    region_sizes = goal.region_sizes

    # time series data
    series = {}
    # contains information about if the asset is bond or stock
    asset_type = {}
    # asset names
    asset_name = []
    only_use_this_assets = []

    super_asset_class_of = dict()
    super_classes_matrix = []
    for i in range(len(regions)):
        super_classes_matrix.append([])
    # contain the market caps values
    market_cap = dict()
    ticker_parent_dict = {}

    for asset in all_assets:
        ticker = asset.tickers.filter(ordering=0).first()
        asset_name.append(ticker.symbol)
        super_asset_class_of[ticker.symbol] = asset.super_asset_class
        series[ticker.symbol] = api.get_all_prices(ticker.symbol)
        ticker_parent_dict[ticker.symbol] = asset.name
        asset_type[ticker.symbol] = 0 if asset.investment_type == 'BONDS' else 1
        market_cap[ticker.symbol] = api.market_cap(ticker)

    # save the data in a pandas table for easy manipulation
    table = DataFrame(series)
    old_columns = list(table)

    # will contain the region custom sizes constrains
    regions_with_bond_and_stock_constrains = dict()
    regions_with_only_stocks_constrains = dict()
    regions_with_only_bonds_constrains = dict()
    region_idx = 0
    default_region_size = region_sizes.get(default_region, 0)

    for ticker_idx in range(0, len(old_columns)):
        if is_from_region(super_asset_class_of, old_columns[ticker_idx], default_region):
            super_classes_matrix[region_idx].append(old_columns[ticker_idx])

    if int(default_region_size * 100) != 0:
        only_use_this_assets.extend(super_classes_matrix[region_idx])
        constrain = create_constrain(super_classes_matrix[region_idx], default_region_size)
        regions_with_bond_and_stock_constrains[default_region] = {"constrain": constrain, "size": default_region_size}

    region_idx += 1

    for region in regions.keys():
        if region == default_region:
            continue

        custom_size = region_sizes.get(region, 0)

        for ticker_idx in range(0, len(old_columns)):
            if is_from_region(super_asset_class_of, old_columns[ticker_idx], region):
                super_classes_matrix[region_idx].append(old_columns[ticker_idx])

        if int(custom_size * 100) != 0:
            only_use_this_assets.extend(super_classes_matrix[region_idx])

            if region in regions_with_only_stocks:
                if int(100 * region_sizes.get(default_region, 0)) == 0:
                    only_use_this_assets.extend(super_classes_matrix[0])
                constrain = create_constrain(super_classes_matrix[region_idx], custom_size)
                regions_with_only_stocks_constrains[region] = {"constrain": constrain, "size": custom_size}
            if region in regions_with_only_bonds:
                if int(100 * region_sizes.get(default_region, 0)) == 0:
                    only_use_this_assets.extend(super_classes_matrix[0])
                constrain = create_constrain(super_classes_matrix[region_idx], custom_size)
                regions_with_only_bonds_constrains[region] = {"constrain": constrain, "size": custom_size}
            elif region == default_region:
                default_region_size += custom_size
            else:
                constrain = create_constrain(super_classes_matrix[region_idx], custom_size)
                regions_with_bond_and_stock_constrains[region] = {"constrain": constrain, "size": custom_size}

        region_idx += 1

    # join all the series in a table, drop missing values
    new_assets_type = []
    views_dict = []
    qs = []
    tau = portfolio_set.tau
    table = table.reindex(index=None, columns=list(set(only_use_this_assets)))
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

    # write restrictions
    json_portfolios = {}
    mw = np.array([])
    tm = 0
    # calculate total market cap
    # create market w
    for ticker_idx in range(0, len(columns)):
        mw = np.append(mw, market_cap[columns[ticker_idx]])
        tm += market_cap[columns[ticker_idx]]

    if tm == 0:
        mw = np.ones([len(mw)]) / len(mw)
    else:
        mw = mw / tm

    print("columns", columns)
    assets_len = len(columns)
    expected_returns = np.array([])

    # calculate expected returns
    for i in range(assets_len):
        er = (1 + np.mean(table[columns[i]].pct_change())) ** 12 - 1
        expected_returns = np.append(expected_returns, er)

    # calculate covariance matrix
    sk_co_var, co_vars = calculate_co_vars(assets_len, table)
    initial_w = mw
    for allocation in list(np.arange(0, 1.01, 0.01)):
        ns = default_region_size
        constrains = []
        # add dual regions
        for cs in regions_with_bond_and_stock_constrains.values():
            constrains.append(cs["constrain"])

        # add only bonds regions
        for cs in regions_with_only_bonds_constrains.values():
            if (1 - allocation) >= cs["size"]:
                constrains.append(cs["constrain"])
            else:
                ns += cs["size"]

        # add only stocks regions
        for cs in regions_with_only_stocks_constrains.values():
            if allocation >= cs["size"]:
                constrains.append(cs["constrain"])
            else:
                ns += cs["size"]

        if ns > 0:
            constrains.append(create_constrain(super_classes_matrix[0], ns))

        print(constrains)
        print(assets_len)
        print(allocation)

        # calculate optimal portfolio for different risks 0 - 100
        new_weights, _mean, var = handle_data(assets_len, expected_returns, sk_co_var, co_vars,
                                              portfolio_set.risk_free_rate, allocation,
                                              new_assets_type, views, qs, tau, constrains, mw,
                                              initial_w, columns)

        initial_w = new_weights
        _mean = float("{0:.4f}".format(_mean)) * 100
        var = float("{0:.4f}".format((var * 100 * 100) ** (1 / 2)))
        allocations = {}

        for column in old_columns:
            if column in columns:
                idx = columns.index(column)
                allocations[ticker_parent_dict[column]] = float("{0:.4f}".format(new_weights[idx]))
            else:
                allocations[ticker_parent_dict[column]] = 0

        json_portfolios["{0:.2f}".format(allocation)] = {
            "allocations": allocations,
            "risk": allocation,
            "expectedReturn": _mean,
            "volatility": var
        }
    return json_portfolios


def calculate_portfolios_for_goal(goal, api=None) -> str:
    if api is None:
        api = DbApi()
    portfolio_set = goal.portfolio_set
    # get all the regions
    all_assets = portfolio_set.asset_classes.all()
    regions = {}

    for asset_class in all_assets:
        new_region = asset_class.super_asset_class.replace("EQUITY_", "").replace("FIXED_INCOME_", "")
        if new_region not in regions:
            regions[new_region] = {"assets_count": 0, "has_bonds": False, "has_stocks": False}
        regions[new_region]["assets_count"] += 1
        if "EQUITY_" in asset_class.super_asset_class:
            regions[new_region]["has_stocks"] = True
        if "FIXED_INCOME_" in asset_class.super_asset_class:
            regions[new_region]["has_bonds"] = True

    if not regions:
        raise Exception("Internal server error please contact your administrator"
                        "(Portfolio set without asset classes [no regions])")

    min_allocation = 0
    max_allocation = 100
    first_asset_type = None

    # filter region with both stock and bonds
    dual_regions = []
    for key, region in regions.items():
        if region["has_bonds"] and region["has_stocks"]:
            dual_regions.append([key, region["assets_count"]])

        if first_asset_type is None:
            first_asset_type = "BOND" if region["has_bonds"] else "STOCK"

    if dual_regions:
        # order region according to assets_count
        dual_regions = list(reversed(sorted(dual_regions, key=lambda x: x[1])))

        # pick first region
        default_region = dual_regions[0][0]
        return calculate_portfolios_dual_region(goal, all_assets, portfolio_set, default_region, regions, api)

    else:
        # there is not dual region, so that means that the portfolio only contains stock o bonds.
        if first_asset_type == "BOND":
            max_allocation = 0
        if first_asset_type == "STOCK":
            min_allocation = 1

    region_sizes = goal.region_sizes
    only_use_this_assets = []
    # time series data
    series = {}
    # contains information about if the asset is bond or stock
    asset_type = {}
    # asset names
    asset_name = []
    super_asset_class_of = dict()
    super_classes_matrix = []

    for i in range(len(regions)):
        super_classes_matrix.append([])
    # contain the market caps values
    market_cap = dict()
    ticker_parent_dict = {}

    for asset in all_assets:
        ticker = asset.tickers.filter(ordering=0).first()
        asset_name.append(ticker.symbol)
        super_asset_class_of[ticker.symbol] = asset.super_asset_class
        series[ticker.symbol] = api.get_all_prices(ticker.symbol)
        ticker_parent_dict[ticker.symbol] = asset.name
        asset_type[ticker.symbol] = 0 if asset.investment_type == 'BONDS' else 1
        market_cap[ticker.symbol] = api.market_cap(ticker)

    # save the data in a pandas table for easy manipulation
    table = DataFrame(series)
    old_columns = list(table)

    # will contain the region custom sizes constrains
    constrains = []
    region_idx = 0

    for region in regions.keys():

        custom_size = region_sizes.get(region, 0)

        for ticker_idx in range(0, len(old_columns)):
            if is_from_region(super_asset_class_of, old_columns[ticker_idx], region):
                super_classes_matrix[region_idx].append(old_columns[ticker_idx])

        if int(custom_size * 100) != 0:
            only_use_this_assets.extend(super_classes_matrix[region_idx])
            constrain = create_constrain(super_classes_matrix[region_idx], custom_size)
            constrains.append(constrain)

        region_idx += 1

    # join all the series in a table, drop missing values
    new_assets_type = []
    views_dict = []
    qs = []
    tau = portfolio_set.tau
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

    # write restrictions
    json_portfolios = {}
    mw = np.array([])
    tm = 0
    # calculate total market cap
    # create market w
    for ticker_idx in range(0, len(columns)):
        mw = np.append(mw, market_cap[columns[ticker_idx]])
        tm += market_cap[columns[ticker_idx]]

    if tm == 0:
        mw = np.ones([len(mw)]) / len(mw)
    else:
        mw = mw / tm

    assets_len = len(columns)
    expected_returns = np.array([])

    # calculate expected returns
    for i in range(assets_len):
        er = (1 + np.mean(table[columns[i]].pct_change())) ** 12 - 1
        expected_returns = np.append(expected_returns, er)

    # calculate covariance matrix
    sk_co_var, co_vars = calculate_co_vars(assets_len, table)
    initial_w = mw
    for allocation in list(np.arange(0, 1.01, 0.01)):
        if max_allocation == 0:
            allocation = 0
        if min_allocation == 1:
            allocation = 1

        # calculate optimal portfolio for different risks 0 - 100
        new_weights, _mean, var = handle_data(assets_len, expected_returns, sk_co_var, co_vars,
                                              portfolio_set.risk_free_rate, allocation,
                                              new_assets_type, views, qs, tau, constrains, mw,
                                              initial_w, columns)

        initial_w = new_weights
        _mean = float("{0:.4f}".format(_mean)) * 100
        var = float("{0:.4f}".format((var * 100 * 100) ** (1 / 2)))
        allocations = {}

        for column in old_columns:
            if column in columns:
                idx = columns.index(column)
                allocations[ticker_parent_dict[column]] = float("{0:.4f}".format(new_weights[idx]))
            else:
                allocations[ticker_parent_dict[column]] = 0

        json_portfolios["{0:.2f}".format(allocation)] = {
            "allocations": allocations,
            "risk": allocation,
            "expectedReturn": _mean,
            "volatility": var
        }
    return json_portfolios


def calculate_portfolios():
    # calculate default portfolio
    yahoo_api = get_api("YAHOO")

    for ps in PortfolioSet.objects.all():
        goal = Goal()
        goal.custom_portfolio_set = ps
        ps.portfolios = json.dumps(calculate_portfolios_for_goal(goal, api=yahoo_api))
        ps.save()

    # calculate portfolios
    for goal in Goal.objects.all():
        if not goal.use_default_portfolio:
            goal.portfolios = json.dumps(calculate_portfolios_for_goal(goal, api=yahoo_api))
            goal.save()


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        calculate_portfolios()
