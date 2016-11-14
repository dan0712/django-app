import logging
import math
import sys
import os
import numpy as np
import pandas as pd
from cvxpy import Variable, sum_entries
from django.conf import settings as sys_settings

from main.models import Ticker, MarketIndex
from portfolios.algorithms.markowitz import markowitz_optimizer_3, markowitz_cost
from portfolios.markowitz_scale import risk_score_to_lambda
from portfolios.prediction.investment_clock import InvestmentClock as Predictor
from portfolios.providers.data.django import DataProviderDjango
from main.models import AssetFeatureValue, GoalMetric

INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL = 'exp_ret'
INSTRUMENT_TABLE_PORTFOLIOSETS_LABEL = 'pids'
INSTRUMENT_TABLE_FEATURES_LABEL = 'features'  # The label in the instruments table for the features column.

_PORTFOLIO_SET_MASK_PREFIX = 'PORTFOLIO-SET_'

# Acceptable modulo multiplier of the unit price for ordering.
ORDERING_ALIGNMENT_TOLERANCE = 0.01

# Minimum percentage of a portfolio that an individual fund can make up. (0.01 = 1%)
# We round to 2 decimal places in the portfolio, so that's why 0.01 is used ATM.
MIN_PORTFOLIO_PCT = 0.03

# Amount we suggest we boost a budget by to make all funds with an original allocation over this amount orderable.
LMT_PORTFOLIO_PCT = 0.05

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

# Raise exceptions if we're doing something dumb with pandas slices
pd.set_option('mode.chained_assignment', 'raise')


def create_portfolio_weights(instruments, min_weights, abs_min):
    pweights = []
    for tid in instruments:
        pweights.append(max(min_weights.get(tid, abs_min), abs_min))
    pweights = np.array(pweights)
    return pweights


def build_instruments(data_provider):
    """
    Builds the information for all the instruments known about in the system.
    :param data_provider: The source of data.
    :return:(covars, instruments, masks)
        - covars is the expected nxn covariance matrix between fund returns over the next 1 year.
        - instruments is a Pandas dataframe indexed by symbol instruments table
            - exp_ret: Annualised expected return of the fund over the next 1 year.
            - ac: The asset class the fund belongs to.
            - price: The current market price of the fund
            - id: The id of the Fund (Ticker model object id)
        - masks are all the group masks that can be used in the constraints.
          It's a pandas DataFrame with column labels for each mask name. There are masks for:
            - Each portfolio set
            - Each AssetFeatureValue in the system
    """
    ac_ps = data_provider.get_asset_class_to_portfolio_set()

    predictor = Predictor(data_provider)
    ers, covars = predictor.get_fund_predictions()

    tickers = data_provider.get_tickers()
    # Much faster building the dataframes once, not appending on iteration.
    irows = []
    for ticker in tickers:
        if ticker.id not in ers:
            logger.warn("Excluding {} from instruments as it has no predictions".format(ticker))
            continue

        irows.append((ticker.symbol,
                      ers[ticker.id],
                      ticker.asset_class.name,
                      data_provider.get_fund_price_latest(ticker=ticker),  # There has to be a daily price, as we have returns
                      data_provider.get_features(ticker=ticker),
                      ac_ps[ticker.asset_class.id],
                      ticker.id
                      ))

    if len(irows) == 0:
        logger.warn("No valid instruments found")
        raise Exception("No valid instruments found")

    # For some reason once I added the exclude arg below, the index arg was ignored, so I have to do it manually after.
    instruments = pd.DataFrame.from_records(irows,
                                            columns=['symbol',
                                                     INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL,
                                                     'ac',
                                                     'price',
                                                     INSTRUMENT_TABLE_FEATURES_LABEL,
                                                     INSTRUMENT_TABLE_PORTFOLIOSETS_LABEL,
                                                     'id'
                                                     ],
                                            ).set_index('symbol')

    masks = get_masks(instruments, data_provider)

    instruments.drop([INSTRUMENT_TABLE_FEATURES_LABEL, INSTRUMENT_TABLE_PORTFOLIOSETS_LABEL], axis=1, inplace=True)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Instruments as dict: {}".format(instruments.to_dict('list')))

    return covars, instruments, masks


def get_instruments(data_provider):
    data = data_provider.get_instrument_cache()
    if data is None:
        data = build_instruments(data_provider)
        data_provider.set_instrument_cache(data)
    return data


def get_masks(instruments, data_provider):
    """
    Returns all the masks for fund features and portfolio sets in the system.
    :param instruments: Information about the funds in the system.
    :param data_provider: The place to get the data about the asset features and portfolio sets available in the system.
    :return: The masks as a pandas dataframe indexed as the instruments input dataframe, columns for each mask id.
    """
    masks = pd.DataFrame(False, index=instruments.index, columns=data_provider.get_asset_feature_values_ids())

    # Add the portfolio set masks
    psid_miloc = {}
    portfolio_sets_ids = data_provider.get_portfolio_sets_ids()
    for psid in portfolio_sets_ids:
        mid = _PORTFOLIO_SET_MASK_PREFIX + str(psid)
        masks[mid] = False
        psid_miloc[psid] = masks.columns.get_loc(mid)

    # Add the feature masks
    fix = instruments.columns.get_loc(INSTRUMENT_TABLE_FEATURES_LABEL) + 1  # Plus 1 for the index entry in the tuple
    psix = instruments.columns.get_loc(INSTRUMENT_TABLE_PORTFOLIOSETS_LABEL) + 1
    for ix, row in enumerate(instruments.itertuples()):
        for fid in row[fix]:
            masks.iloc[ix, masks.columns.get_loc(fid)] = True
        for psid in row[psix]:
            masks.iloc[ix, psid_miloc[psid]] = True
    return masks


def get_settings_masks(settings, masks):
    '''
    Removes any funds that do not fit within our metric constraints.
    :param settings: The goal.active_settings we want to modify the global masks for
    :param masks: The global asset feature masks
    :return: (settings_symbol_ixs, cvx_masks)
        - settings_symbol_ixs: A list of ilocs into the masks index for the symbols used in this setting.
        - cvx_masks: A dict from mask name to list of indicies in the setting_symbols list that match this mask name.
    '''
    removals = np.array([False] * len(masks))

    # logger.debug("Creating Settings masks from global masks: {}".format(masks))
    fids = []
    metrics = settings.get_metrics_all()

    for metric in metrics:
        if metric.type == 0:
            if math.isclose(metric.configured_val, 0.0):
                # Saying a minimum percentage of 0% is superfluous.
                if metric.comparison > 0:
                    removals |= masks[metric.feature.id]
                    logger.debug("Removing instruments for feature: {} ".format(metric.feature))
            elif math.isclose(metric.configured_val, 1.0) and metric.comparison == 2:
                # Saying a maximum percentage of 100% is superfluous
                pass
            else:
                if metric.feature.id not in masks.columns:
                    raise Unsatisfiable("The are no funds that satisfy metric: {}".format(metric))
                fids.append(metric.feature.id)

    # Do the removals
    settings_mask = np.logical_not(removals)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Mask for settings: {} after removals: {} ({} items)".format(settings, settings_mask, len(settings_mask.nonzero())))

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Fund positions: {}".format(settings_mask.nonzero()[0].tolist()))

    # Only use the instruments from the specified portfolio set.
    settings_mask &= masks[_PORTFOLIO_SET_MASK_PREFIX + str(settings.goal.portfolio_set.id)]

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Usable positions according to our portfolio: {}".format(settings_mask.nonzero()[0].tolist()))

    # Convert a global feature masks mask into an index list suitable for the optimisation variables.
    cvx_masks = {fid: masks.loc[settings_mask, fid].nonzero()[0].tolist() for fid in fids}

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("CVX masks for settings: {}: {}".format(settings, cvx_masks))

    return settings_mask.nonzero()[0].tolist(), cvx_masks


def get_core_constraints(nvars):
    """
    Creates the core cvxpy constraints and optimisation variables for any portfolio optimisation calculation.
    :param nvars: The number of optimisation variables to create.
    :return: (xs, constraints)
        - xs: The list of cvxpy variables that we will optimise for.
        - constraints: The core constraints suitable for cvxpy
    """
    # Create the list of variables that we will optimise for.
    xs = Variable(nvars)

    # Start with the constraint that all must add to 1
    constraints = [sum_entries(xs) == 1]

    return xs, constraints


def get_metric_constraints(settings, cvx_masks, xs, overrides=None, data_provider=None):
    """
    Adds the constraints to be used by cvxpy coming from the metrics for this goal.
    :param settings: Details of the settings you want the constraints for
    :param cvx_masks: A dict of all the settings-specific cvxpy iloc lists against the settings_symbols for each mask name.
    :param xs: The list of cvxpy variables we are optimising
    :param overrides: An associative collection of key -> overridden value, where key can be any feature id, or the
                      string 'risk_score' to override the risk score.
    :return: (lambda, constraints)
    """
    constraints = []
    risk_score = None

    metrics = settings.get_metrics_all()
    for metric in metrics:
        if metric.type == 1:
            if overrides:
                risk_score = overrides.get("risk_score", metric.configured_val)
            else:
                risk_score = metric.configured_val
        elif metric.type == 0:  # Portfolio Mix
            if overrides:
                val = overrides.get(metric.feature.id, metric.configured_val)
            else:
                val = metric.configured_val
            # Non-inclusions are taken care of in the settings mask, so ignore those constraints.
            if math.isclose(val, 0.0):
                continue
            # Saying a maximum percentage of 100% is superfluous, so ignore those constraints.
            if math.isclose(val, 1.0) and metric.comparison == 2:
                continue

            feature_assets = cvx_masks[metric.feature.id]
            # If we have no possible symbols, and we have a metric with a non-zero allocation, fail.
            if len(feature_assets) == 0:
                if metric.comparison != GoalMetric.METRIC_COMPARISON_MAXIMUM:
                    emsg = "Settings metric: {} is not satisfiable. There are no funds available to fulfil the constraint."
                    raise Unsatisfiable(emsg.format(metric))
                # If we don't have assets for the feature, don't worry about inserting maximum constraints,
                # as the allocation will always be zero for that feature.
                continue
            if metric.comparison == 0:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Adding constraint that symbols: {} must be minimum {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) >= val)
            elif metric.comparison == 1:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Adding constraint that symbols: {} must be exactly {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) == val)
            elif metric.comparison == 2:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Adding constraint that symbols: {} must be maximum {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) <= val)
            else:
                raise Exception("Unknown metric comparison value: {} found for settings: {}".format(metric.comparison, settings))
        else:
            raise Exception("Unknown metric type: {} found for settings: {}".format(metric.type, settings))

    if risk_score is None:
        raise Exception("Risk score metric could not be found for settings: {}".format(settings))

    lambda_risk = risk_score_to_lambda(risk_score=risk_score, data_provider=data_provider)
    return lambda_risk, constraints


class Unsatisfiable(Exception):
    def __init__(self, msg, req_funds=None):
        self.msg = str(msg)
        self.req_funds = req_funds

    def __str__(self):
        return self.msg


def optimize_settings(settings, idata, data_provider, execution_provider):
    """
    Calculates the portfolio weights for a given settings object
    :param settings: GoalSettings object
    :param idata: Global instrument data
    :return: (weights, cost, xs, lam, constraints, settings_instruments, settings_symbol_ixs, lcovars)
            - lcovars - A Pandas dataframe indexed in both directions on ticker id.
    """
    # Optimise for the instrument weights given the constraints
    result = calc_opt_inputs(settings=settings,
                             idata=idata,
                             data_provider=data_provider,
                             execution_provider=execution_provider)
    xs, lam, constraints, settings_instruments, settings_symbol_ixs, lcovars = result
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Optimising settings using lambda: {}, \ncovars: {}".format(lam, lcovars))

    mu = settings_instruments[INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL]
    weights, cost = markowitz_optimizer_3(xs, lcovars.values, lam, mu.values, constraints)

    if not weights.any():
        raise Unsatisfiable("Could not find an appropriate allocation for Settings: {}".format(settings))

    return weights, cost, xs, lam, constraints, settings_instruments, settings_symbol_ixs, lcovars


def calc_opt_inputs(settings, idata, data_provider, execution_provider, metric_overrides=None):
    '''
    Calculates the inputs suitable for our portfolio optimiser based on global data and details from the settings
    object.
    :param settings: A GoalSettings object
    :param idata: The global instrument data
    :param metric_overrides:
    :return:
    '''
    # Get the global instrument data
    covars, instruments, masks = idata

    # Convert the settings into a constraint based on a mask for the instruments appropriate for the settings given
    settings_symbol_ixs, cvx_masks = get_settings_masks(settings=settings, masks=masks)
    if len(settings_symbol_ixs) == 0:
        raise Unsatisfiable("No assets available for settings: {} given it's constraints.".format(settings))
    xs, constraints = get_core_constraints(len(settings_symbol_ixs))
    lam, mconstraints = get_metric_constraints(settings=settings,
                                               cvx_masks=cvx_masks,
                                               xs=xs,
                                               overrides=metric_overrides,
                                               data_provider=data_provider)
    constraints += mconstraints

    settings_instruments = instruments.iloc[settings_symbol_ixs]

    # Add the constraint that they must be over the current lots held less than 1 year.
    tax_min_weights = execution_provider.get_asset_weights_held_less_than1y(settings.goal,
                                                                            data_provider.get_current_date())
    pweights = create_portfolio_weights(settings_instruments['id'].values,
                                        min_weights=tax_min_weights,
                                        abs_min=0)
    constraints += [xs >= pweights]

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Got constraints for settings: {}. Active symbols:{}".format(settings, settings_symbol_ixs))

    lcovars = covars.iloc[settings_symbol_ixs, settings_symbol_ixs]

    return xs, lam, constraints, settings_instruments, settings_symbol_ixs, lcovars


def extract_risk_setting(settings):
    metrics = settings.get_metrics_all()
    risk_score = 0
    for metric in metrics:
        if metric.type == GoalMetric.METRIC_TYPE_RISK_SCORE:
            risk_score = metric.configured_val
            break
    risk_profile = round(risk_score * 100)
    return risk_profile


def get_ticker_ids_for_symbols(symbol_list):
    id_list = list()
    ticker_to_id = dict()
    id_to_ticker = dict()
    for symbol in symbol_list:
        count = Ticker.objects.filter(symbol=symbol).count()
        if count == 1:
            ticker = Ticker.objects.get(symbol=symbol)
            id_list.append(ticker.id)
            ticker_to_id[symbol] = ticker.id
            id_to_ticker[ticker.id] = symbol
    return (id_list, ticker_to_id, id_to_ticker)


def build_weights(source_weights, list_ids, id_to_ticker):
    weights = list()
    for id in list_ids:
        weight = source_weights.ix[id_to_ticker[id]]
        weight = 0 if pd.isnull(weight) else weight
        weights.append(weight)
    return np.array(weights)


def update_expected_return(data, settings_instruments, id_to_ticker):
    for row_index in settings_instruments.index.tolist():
        current_row = settings_instruments.ix[row_index]
        id = current_row['id']
        if id in id_to_ticker:
            symbol = id_to_ticker[id]
            risk_premia = float(data.ix[symbol])
            settings_instruments.ix[row_index,'exp_ret'] = risk_premia
    return settings_instruments


def calculate_portfolio(settings, data_provider, execution_provider, idata=None):
    """
    Calculates the instrument weights to use for a given goal settings.
    :param settings: goal.active_settings to calculate the portfolio for.
    :return: (weights, er, variance) All values will be None if no suitable allocation can be found.
             - weights: A Pandas series of weights for each instrument.
             - er: Expected return of portfolio
             - stdev: stdev of portfolio
    """
    if idata is None:
        idata = get_instruments(data_provider)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Calculating portfolio for settings: {}".format(settings))


    '''risk_profile = extract_risk_setting(settings)
    risk_profile_data = pd.read_csv(os.getcwd() + "/data/risk_profiles.csv", index_col=0)
    ticker_ids, ticker_to_id, id_to_ticker = get_ticker_ids_for_symbols(risk_profile_data.index.tolist())
    weights = build_weights(risk_profile_data.iloc[:, risk_profile], ticker_ids, id_to_ticker)

    covars, instruments, masks = idata
    settings_symbol_ixs, cvx_masks = get_settings_masks(settings=settings, masks=masks)

    lcovars = covars.iloc[settings_symbol_ixs, settings_symbol_ixs]
    settings_instruments = instruments.iloc[settings_symbol_ixs]

    risk_premia_data = pd.read_csv(os.getcwd() + "/data/expected_return.csv", index_col=0)
    settings_instruments = update_expected_return(risk_premia_data, settings_instruments, id_to_ticker)'''

    odata = optimize_settings(settings, idata, data_provider, execution_provider)
    weights, cost, xs, lam, constraints, settings_instruments, settings_symbol_ixs, lcovars = odata
    # Find the orderable weights. We don't align as it's too cpu intensive ATM.
    # We do however need to do the 3% cutoff so we don't end up with tiny weights.
    weights, cost = make_orderable(weights,
                                   cost,
                                   xs,
                                   lcovars.values,
                                   settings_instruments[INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL].values,
                                   lam,
                                   constraints,
                                   settings,
                                   # We use the current balance (including pending deposits).
                                   settings.goal.current_balance,
                                   settings_instruments['price'],
                                   align=False)

    stats = get_portfolio_stats(settings_instruments, lcovars, weights)
    return stats


def calculate_portfolios(setting, data_provider, execution_provider):
    """
    Calculate a list of 101 portfolios ranging over risk score.
    :param setting: The settig we want to generate portfolios for.
    :param data_provider: Where to get the data
    :param execution_provider:
    :raises Unsatisfiable: If no single satisfiable portfolio could be found.
    :return: A list of 101 (risk_score, portfolio) tuples
            - risk_score [0-1] in steps of 0.01
            - portfolio is the same as the return value of calculate_portfolio.
                portfolio will be None if no satisfiable portfolio could be found for this risk_score
    """
    logger.debug("Calculate Portfolios Requested")
    try:
        idata = get_instruments(data_provider)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Got instruments")
        # We don't need to recalculate the inputs for every risk score, as the risk score is just passed back.
        # We can do that directly
        opt_inputs = calc_opt_inputs(setting, idata, data_provider, execution_provider)
        xs, lam, constraints, setting_instruments, setting_symbol_ixs, lcovars = opt_inputs
        sigma = lcovars.values
        mu = setting_instruments[INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL].values
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Optimising for 100 portfolios using mu: {}\ncovars: {}".format(mu, lcovars))

        # TODO: Use a parallel approach here.
        portfolios = []
        found = False
        max_funds = 0  # Maximum required amount off any of the unsatisfiable errors
        for risk_score in list(np.arange(0, 1.01, 0.01)):
            lam = risk_score_to_lambda(risk_score=risk_score, data_provider=data_provider)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Doing risk_score: {}, giving lambda: {}".format(risk_score, lam))
            try:
                weights, cost = markowitz_optimizer_3(xs, sigma, lam, mu, constraints)
                if not weights.any():
                    raise Unsatisfiable("Could not find an appropriate allocation for Settings: {}".format(setting))

                # Find the orderable weights. We don't align as it's too cpu intensive ATM.
                # We do however need to do the 3% cutoff so we don't end up with tiny weights.
                weights, cost = make_orderable(weights,
                                               cost,
                                               xs,
                                               sigma,
                                               mu,
                                               lam,
                                               constraints,
                                               setting,
                                               # We use the current balance (including pending deposits).
                                               setting.goal.current_balance,
                                               setting_instruments['price'],
                                               align=False)

                # Convert to our statistics for our portfolio.
                portfolios.append((risk_score, get_portfolio_stats(setting_instruments,
                                                                   lcovars,
                                                                   weights)))
                found = True

            except Exception as e:
                e = Unsatisfiable(e)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("No allocation possible for lambda: {}".format(lam))
                last_err = e
                if e.req_funds:
                    max_funds = max(max_funds, e.req_funds)
                portfolios.append((risk_score, None))

        if not found:
            emsg = "No suitable portfolio could be found for any risk score. Last reason: {}"
            raise Unsatisfiable(emsg.format(last_err), max_funds if max_funds else None)

    except:
        logger.exception("Problem calculating portfolio for setting: {}".format(setting))
        raise

    return portfolios


def current_stats_from_weights(weights, data_provider):
    """
    :param weights: A list of (ticker_id, weight) tuples. Weights must add to <= 1.
    :return: (portfolio_er, portfolio_stdev, {ticker_id: ticker_variance})
    """
    covars, instruments, masks = get_instruments(data_provider)

    ix = instruments.set_index('id').index
    ilocs = []
    res = {}
    wts = []
    for tid, weight in weights:
        if tid not in ix:
            raise Unsatisfiable("Statistics for asset id: {} are not currently available.".format(tid))
        iloc = ix.get_loc(tid)
        ilocs.append(iloc)
        res[tid] = covars.iloc[iloc, iloc]
        wts.append(weight)

    # Generate portfolio stdev and expected return
    nweights = np.array(wts)
    lcovars = covars.iloc[ilocs, ilocs]
    lers = instruments[INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL].iloc[ilocs]
    er = nweights.dot(lers)
    variance = nweights.dot(lcovars).dot(nweights.T)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Generated portfolio expected return of {} using current asset returns: {}".format(er, lers))
        logger.debug("Generated portfolio variance of {} using current asset covars: {}".format(variance, lcovars))

    return er, variance ** (1 / 2), res


def get_portfolio_stats(instruments, covars, weights):
    """
    :param instruments: The pandas dataframe of instrument data containing only the instruments matching the weights
                        and covars.
    :param covars: The covars for the weights provided
    :param weights: The weights of each instrument.
    :return: (weights, er, stdev)
            - weights is Pandas series of weights indexed on Ticker id
            - er is the 12 month expected return of the portfolio
            - stdev is the 12 month stdev of the portfolio returns
    """

    ret_weights = pd.Series(weights, index=instruments['id'])

    # Filter out assets with no allocation
    ret_weights = ret_weights[ret_weights > 0.005]

    # Generate portfolio variance and expected return
    er = weights.dot(instruments[INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL])
    variance = weights.dot(covars).dot(weights.T)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Generated asset weights: {}".format(weights))
        logger.debug("Generated portfolio expected return of {} using asset returns: {}".format(
            er,
            instruments[INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL]))
        logger.debug("Generated portfolio variance of {} using asset covars: {}".format(variance, covars))

    # Convert variance to stdev
    return ret_weights, er, variance ** (1 / 2)


def make_orderable(weights, original_cost, xs, sigma, mu, lam, constraints, settings, budget, prices, align=True):
    """
    Turn the raw weights into orderable units
    There are three costs here:
    - Markowitz cost
    - Variation from budget
    - Variation from constraints (drift)
    For now we just minimize the Markowitz cost, but we can be smarter.

    :param weights: A 1xn numpy array of the weights we need to perturbate to fit into orderable units.
    :param original_cost: The pre-ordering Markowitz cost
    :param xs: The cvxpy variables (length n) we can feed to the optimizer
    :param sigma: A nxn numpy array of the covariances matrix between assets
    :param mu: A 1xn numpy array of the expected returns per asset
    :param lam: The Markowitz risk appetite constant
    :param constraints: The existing constraints we must adhere to
    :param settings: The settings we are making this portfolio orderable for.
    :param budget: The budget we have to make this portfolio orderable.
    :param prices: The prices of each asset.
    :param align: Perform the alignment to orderable quantities phase.

    :raises Unsatifiable if at any point a satisfiable portfolio cannot be found.

    :return: (weights, cost)
        - weights: A 1xn numpy array of the new symbol weights that should align to orderable units given the passed prices.
          This will always be set, otherwise Unsatisfiable will be raised.
        - cost is the new Markowitz cost
    """

    def aligned(i):
        """
        Returns true if the weight at index ix produces an order qty with remainder within 1% of the orderable qty.
        :param i: THe index into the weights and prices arrays
        """
        rem = (weights[i] * budget) % prices[i]
        return (rem < prices[i] * ORDERING_ALIGNMENT_TOLERANCE) or (rem > prices[i] * (1 - ORDERING_ALIGNMENT_TOLERANCE))

    def bordering(i):
        """
        Returns the two orderable weights for this index
        - The one rounded down, and the one rounded up from the input weight.
        :param i: The index of interest
        """
        qty = (weights[i] * budget) // prices[i]
        return ((qty * prices[i]) / budget), (((qty + 1) * prices[i]) / budget)

    # Copy the constraints because we mess with them in here, and we don't want that visible
    constraints = constraints[:]

    # We only ever want weights over The MIN_PORTFOLIO_PCT.
    inactive = weights < MIN_PORTFOLIO_PCT

    # Deactivate any instruments that didn't reach at least orderable quantity of 1.
    # TODO: BB-26: Take into account minimum current holdings of each stock and minimum holding qty and minimum orderable qty.
    inactive_unit = inactive | (((weights * budget) / prices) < 1)

    # If some are not at orderable levels, but are over our acceptable inclusion limit, find the budget required to get
    # all assets that over LMT_PORTFOLIO_PCT to orderable levels.
    if (inactive != inactive_unit).any():
        interested = weights > LMT_PORTFOLIO_PCT
        ovr_lmt = weights[interested]
        req_mult = np.min(ovr_lmt)
        req_units = np.zeros_like(weights)
        req_units[interested] = np.ceil(ovr_lmt * req_mult)
        # TODO: Figure out the ordering costs of the assets for this customer at this point based on current holdings,
        # TODO: costs per asset and units to purchase. Notify these costs to the user.
        req_budget = np.sum(req_units * prices)

        # If our budget is over the minimum required, keep trying the optimisation, otherwise, return nothing.
        if budget < req_budget:
            emsg = "The budget of {0} {1} is insufficient to purchase all the assets in the portfolio with allocated " \
                   "proportions over {2}%. Please increase the budget to at least {3} {1} to purchase this portfolio."
            raise Unsatisfiable(emsg.format(budget, sys_settings.SYSTEM_CURRENCY, LMT_PORTFOLIO_PCT * 100, math.ceil(req_budget)),
                                math.ceil(req_budget))

    inactive_ilocs = inactive_unit.nonzero()[0].tolist()
    if len(inactive_ilocs) > 0:
        constraints.append(xs[inactive_ilocs] == 0)
        # Optimise again given the new constraints
        weights, cost = markowitz_optimizer_3(xs, sigma, lam, mu, constraints)
        # If we don't get an orderable amount here, there's nothing left to do.
        if not weights.any():
            emsg = "Could not find orderable portfolio for settings: {} once I removed assets below ordering threshold"
            raise Unsatisfiable(emsg.format(settings))
    else:
        cost = original_cost

    # If we don't want to perform the alignment stage, return now.
    if not align:
        return weights, cost

    # Create a collection of all instruments that are to be included, but the weights are currently not on an orderable
    # quantity.
    # Find the minimum Markowitz cost off all the potential portfolio combinations that could be generated from a round
    # up and round down of each fund involved to orderable quantities.
    indicies = []
    tweights = []
    aligned_weight = 0.0  # Weight of the already aligned component.
    for ix, weight in enumerate(weights):
        if inactive[ix]:
            continue
        if aligned(ix):
            aligned_weight += weight
        indicies.append(ix)
        tweights.append(bordering(ix))

    elems = len(indicies)
    wts = np.expand_dims(weights, axis=0)
    mcw = np.copy(wts)
    if elems > 0:
        rounds = 2 ** elems
        min_cost = sys.float_info.max
        # TODO: This could be done parallel
        for mask in range(rounds):
            # Set the weights for this round
            for pos, tweight in enumerate(tweights):
                wts[0, indicies[pos]] = tweight[(mask & (1 << pos)) > 0]
            # Exclude this combination if the sum of the weights is over the 1 (The budget).
            if (np.sum(wts) + aligned_weight) > 1.00001:
                continue
            new_cost = markowitz_cost(wts, sigma, lam, mu)
            if new_cost < min_cost:
                mcw = np.copy(wts)
                min_cost = new_cost
        wts = mcw

    if not wts.any():
        emsg = "Could not find an appropriate allocation given ordering constraints for settings: {} "
        raise Unsatisfiable(emsg.format(settings))

    logger.info('Ordering cost for settings {}: {}, pre-ordering val: {}'.format(settings.id,
                                                                                 min_cost - original_cost,
                                                                                 original_cost))

    return wts[0], min_cost
