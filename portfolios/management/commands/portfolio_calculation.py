import sys
import math
import datetime
import logging

import pandas as pd
import numpy as np
from cvxpy import sum_entries, Variable
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.core.cache import cache

from main import redis

from main.models import (
    SYSTEM_CURRENCY,
    Goal, Ticker, AssetFeatureValue, 
    MarkowitzScale, PortfolioSet,
)

from portfolios.BL_model.bl_model import bl_model, markowitz_optimizer_3, markowitz_cost
from portfolios.api.yahoo import DbApi
from portfolios.bl_model import calculate_co_vars
from portfolios.profile_it import do_cprofile


TYPE_MASK_PREFIX = 'TYPE_'
ETHICAL_MASK_NAME = 'ETHICAL'
REGION_MASK_PREFIX = 'REGION_'
PORTFOLIO_SET_MASK_PREFIX = 'PORTFOLIO-SET_'
ETF_MASK_NAME = 'ETF'

# Acceptable modulo multiplier of the unit price for ordering.
ORDERING_ALIGNMENT_TOLERANCE = 0.01

# Minimum percentage of a portfolio that an individual fund can make up. (0.01 = 1%)
# We round to 2 decimal places in the portfolio, so that's why 0.01 is used ATM.
MIN_PORTFOLIO_PCT = 0.01

# Amount we suggest we boost a budget by to make all funds with an original allocation over this amount orderable.
LMT_PORTFOLIO_PCT = 0.05

# How many pricing samples do we need to make the statistics valid?
MINIMUM_PRICE_SAMPLES = 12

logger = logging.getLogger('betasmartz.portfolio_calculation')
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

# Raise exceptions if we're doing something dumb with pandas slices
pd.set_option('mode.chained_assignment', 'raise')


def months_between(date1, date2):
    if date1 > date2:
        date1, date2 = date2, date1
    m1 = date1.year*12 + date1.month
    m2 = date2.year*12 + date2.month
    return m2 - m1


def build_instruments(api=DbApi()):
    """
    Builds all the instruments know about in the system.
    Have global pandas tables of all the N instruments in the system, and operate on these tables through masks.
        - N x 5 Instruments table
            - Column 1 (exp_ret): Annualised expected return
            - Column 2 (mkt_cap): Market cap or AUM in system currency
            - Column 3 (ac): The asset class the instrument belongs to.
            - Column 4 (price): The current market midprice
            - Column 5 (id): The id of the Ticker model object
        - Covariance matrix (N x N)
        - N x M array of views defined on instruments
        - M x 1 array of expected returns per view.
    Have the following precomputed masks against the instruments table:
        - Each portfolio set
        - Each region
        - Ethical
        - Asset type (Stock ETF, Bond ETF, Mutual Fund)
    :param api: The source of data for the instrument prices.
    :return:(covars, samples, instruments, masks)
        - covars is the covariance matrix between instruments
        - samples is the number of samples that was used to build the covariance matrix.
        - instruments is the instruments table
        - masks are all the group masks that can be used in the constraints.
          It's a pandas DataFrame with column labels for each mask name.
    """
    ac_ps = defaultdict(list)
    # Build the asset_class -> portfolio_sets mapping
    for ps in PortfolioSet.objects.all():
        for ac in ps.asset_classes.all():
            ac_ps[ac.id].append(ps.id)

    tickers = Ticker.objects.all()
    # Much faster building the dataframes once, not appending on iteration.
    irows = []
    ccols = []

    # the minimum index that has data for all symbols.
    minix = 0

    for ticker in tickers:
        # TODO: Get the current price from the daily prices table, not monthly.
        prices = api.get_all_prices(ticker.symbol, currency=ticker.currency)
        if not minix:
            minix = -prices.shape[0]

        # Make sure we have the minimum data to make the statistics meaningful.
        isnulls = pd.isnull(prices)
        if isnulls.iloc[-MINIMUM_PRICE_SAMPLES:].any():
            emsg = "Removing symbol: {} from candidates as it has only {} available prices in the last {} samples."
            logger.warn(emsg.format(ticker.symbol, prices.iloc[-MINIMUM_PRICE_SAMPLES:].count(), MINIMUM_PRICE_SAMPLES))
            continue
        mc = api.market_cap(ticker)
        if mc is None:
            emsg = "Removing symbol: {} from candidates as it has no market cap available"
            logger.warn(emsg.format(ticker.symbol))
            continue

        # Build annualised expected return
        first_valid = isnulls.argmin()
        mths = months_between(first_valid, prices.index[-1]) + 1
        er = (((prices.iloc[-1] - prices[first_valid]) / prices[first_valid]) / (mths / 12))
        logger.debug("Built expected return {} for {} using {} months of data.".format(er, ticker.symbol, mths))
        #er = (1 + ccols[-1].pct_change().mean()) ** 12 - 1

        # We need there to be no gaps in the prices, so our covariance calculation is correct. So find the min index
        # that is common to all symbols.
        for i in range(-(MINIMUM_PRICE_SAMPLES-1), minix-1, -1):
            if pd.isnull(prices[i]):
                minix = max(minix, i+1)
                break

        # Data good, so add the symbol
        ccols.append(prices)

        irows.append((ticker.symbol,
                      er,
                      mc,
                      ticker.asset_class.name,
                      prices.iloc[-1],
                      ticker.features.values_list('id', flat=True),
                      ac_ps[ticker.asset_class.id],
                      ticker.id,
                      ))

    if len(ccols) == 0:
        logger.warn("No valid instruments found")
        raise Exception("No valid instruments found")

    # Filter the table to be only complete.
    ctable = pd.concat(ccols, axis=1).iloc[minix:, :]

    # For some reason once I added the exclude arg below, the index arg was ignored, so I have to do it manually after.
    instruments = pd.DataFrame.from_records(irows,
                                            columns=['symbol', 'exp_ret', 'mkt_cap', 'ac', 'price', 'features', 'pids', 'id'],
                                            exclude=['features', 'pids']).set_index('symbol')

    masks = pd.DataFrame(False, index=instruments.index, columns=AssetFeatureValue.objects.values_list('id', flat=True))

    # Add this symbol to the appropriate portfolio set masks
    psid_miloc = {}
    for psid in PortfolioSet.objects.values_list('id', flat=True):
        mid = PORTFOLIO_SET_MASK_PREFIX + str(psid)
        masks[mid] = False
        psid_miloc[psid] = masks.columns.get_loc(mid)
    for ix, row in enumerate(irows):
        for fid in row[5]:
            masks.iloc[ix, masks.columns.get_loc(fid)] = True
        for psid in row[6]:
            masks.iloc[ix, psid_miloc[psid]] = True

    # For now we are using the old covariance method as some funds do not have 12 months data, and the old way allows
    # differing sample lengths..
    # TODO: Get rid of this and use the standard pandas covariance method.
    sk_co_var, co_vars = calculate_co_vars(ctable.shape[1], ctable)
    co_vars = pd.DataFrame(co_vars, index=instruments.index, columns=instruments.index)
    #samples = 12

    # Drop dates that have nulls for some symbols.
    # TODO: Have some sanity check over the data. Make sure it's recent, gap free and with enough samples.
    #ptable = ctable.dropna()

    logger.debug("Prices as table: {}".format(ctable.to_dict('list')))
    #logger.debug("Prices as list: {}".format(ptable.values.tolist()))

    #co_vars = ctable.cov()
    samples = ctable.shape[0]
    logger.debug("Market Caps as table: {}".format(instruments['mkt_cap'].to_dict()))
    logger.debug("Using symbols: {}".format([(row[0] + "[{}]".format(ix), row[5]) for ix, row in enumerate(irows)]))

    return co_vars, samples, instruments, masks


def get_instruments(api=DbApi()):
    key = redis.KEY_INSTRUMENTS(datetime.date.today().isoformat())
    data = cache.get(key)

    if data is None:
        data = build_instruments(api)
        cache.set(key, data, timeout=60*60*24)

    return data


def get_settings_masks(settings, masks):
    '''
    :param settings: The settings we want to modify the global masks for
    :param masks: The global asset feature masks
    :return: (settings_symbol_ixs, cvx_masks)
        - settings_symbol_ixs: A list of ilocs into the masks index for the symbols used in this setting.
        - cvx_masks: A dict from mask name to list of indicies in the setting_symbols list that match this mask name.
    '''
    removals = np.array([False] * len(masks))

    # logger.debug("Creating Settings masks from global masks: {}".format(masks))
    fids = []

    for metric in settings.metric_group.metrics.all():
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
                fids.append(metric.feature.id)

    # Do the removals
    settings_mask = np.logical_not(removals)
    logger.debug("Mask for settings: {} after removals: {} ({} items)".format(settings, settings_mask, len(settings_mask.nonzero())))

    # Only use the instruments from the specified portfolio set.
    settings_mask &= masks[PORTFOLIO_SET_MASK_PREFIX + str(settings.goal.portfolio_set.id)]

    logger.debug("Usable indicies in our portfolio: {}".format(settings_mask.nonzero()[0].tolist()))

    # Convert a global feature masks mask into an index list suitable for the optimisation variables.
    cvx_masks = {fid: masks.loc[settings_mask, fid].nonzero()[0].tolist() for fid in fids}
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

    # Add the constraint that all must be positive
    constraints.append(xs >= 0)

    return xs, constraints


def get_metric_constraints(settings, cvx_masks, xs, overrides=None):
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
    for metric in settings.metric_group.metrics.all():
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
            if len(feature_assets) == 0 and metric.comparison != 2:
                raise Unsatisfiable("Settings metric: {} is not satisfiable.".format(metric))
            if metric.comparison == 0:
                logger.debug("Adding constraint that symbols: {} must be minimum {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) >= val)
            elif metric.comparison == 1:
                logger.debug("Adding constraint that symbols: {} must be exactly {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) == val)
            elif metric.comparison == 2:
                logger.debug("Adding constraint that symbols: {} must be maximum {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) <= val)
            else:
                raise Exception("Unknown metric comparison value: {} found for settings: {}".format(metric.comparison, settings))
        else:
            raise Exception("Unknown metric type: {} found for settings: {}".format(metric.type, settings))

    if risk_score is None:
        raise Exception("Risk score metric could not be found for settings: {}".format(settings))

    return risk_score_to_lambda(risk_score), constraints


def risk_score_to_lambda(risk_score):
    # Turn the risk score into a markowitz lambda
    scale = MarkowitzScale.objects.order_by('-date').first()
    if scale is None:
        raise Exception("No Markowitz limits available. Cannot convert The risk score into a Markowitz lambda.")
    if scale.date < (datetime.datetime.today() - datetime.timedelta(days=7)).date():
        logger.warn("Most recent Markowitz scale is from {}.".format(scale.date))
    return scale.a * math.pow(scale.b, (risk_score * 100) - 50) + scale.c


def lambda_to_risk_score(lam):
    # Turn the markowitz lambda into a risk score
    scale = MarkowitzScale.objects.order_by('-date').first()
    if scale is None:
        raise Exception("No Markowitz limits available. Cannot convert The Markowitz lambda into a risk score.")
    if scale.date < (datetime.datetime.today() - datetime.timedelta(days=7)).date():
        logger.warn("Most recent Markowitz scale is from {}.".format(scale.date))
    return (math.log((lam - scale.c)/scale.a, scale.b) + 50) / 100


def get_market_caps(instruments):
    """
    Get a set of initial weights based on relative market capitalisation
    :param instruments: The instruments table
    :return: A pandas series indexed as the instruments table containing the initial unoptimised instrument weights.
    """
    interested = instruments['mkt_cap']
    total_market = interested.sum()
    if total_market == 0:
        return 0
    return interested / total_market


def get_views(portfolio_set, instruments):
    """
    Return the views that are appropriate for a given portfolio set.
    :param portfolio_set: The portfolio set to get the views for.
    :param instruments: The n x d pandas dataframe with n instruments and their d data columns.
    :return: (views, view_rets)
        - views is a masked nxm numpy array corresponding to m investor views on future asset movements
        - view_rets is a mx1 numpy array of expected returns corresponding to views.
    """
    # TODO: We should get the cached views per portfolio set from redis
    ps_views = portfolio_set.views.all()
    views = np.zeros((len(ps_views), instruments.shape[0]))
    qs = []
    masked_views = []
    for vi, view in enumerate(ps_views):
        header, view_values = view.assets.splitlines()

        header = header.split(",")
        view_values = view_values.split(",")

        for sym, val in zip(header, view_values):
            _symbol = sym.strip()
            try:
                si = instruments.index.get_loc(_symbol)
                views[vi][si] = float(val)
            except KeyError:
                mstr = "Ignoring view: {} in portfolio set: {} as symbol: {} is not active"
                logger.debug(mstr.format(vi, portfolio_set.name, _symbol))
                masked_views.append(vi)
        qs.append(view.q)

    views = np.delete(views, masked_views, 0)
    qs = np.delete(np.asarray(qs), masked_views, 0)
    return views, qs


#@do_cprofile
def calculate_portfolios(setting, api=DbApi()):
    """
    Calculate a list of 101 portfolios ranging over risk score.
    :param setting: The settig we want to generate portfolios for.
    :param api: Where to get the data
    :raises Unsatisfiable: If no single satisfiable portfolio could be found.
    :return: A list of 101 (risk_score, portfolio) tuples
            - risk_score [0-1] in steps of 0.01
            - portfolio is the same as the return value of calculate_portfolio.
                portfolio will be None if no satisfiable portfolio could be found for this risk_score
    """
    logger.debug("Calculate Portfolios Requested")
    try:
        idata = get_instruments(api)
        logger.debug("Got instruments")
        # We don't need to recalculate the inputs for every risk score, as the risk score is just passed back.
        # We can do that directly
        opt_inputs = calc_opt_inputs(setting, idata)
        xs, sigma, mu, _, constraints, goal_instruments, goal_symbol_ixs, instruments, lcovars = opt_inputs
        logger.debug("Optimising for 100 portfolios using mu: {}\ncovars: {}\nsigma: {}".format(mu, lcovars, sigma))
        # TODO: Use a parallel approach here.
        portfolios = []
        found = False
        for risk_score in list(np.arange(0, 1.01, 0.01)):
            lam = risk_score_to_lambda(risk_score)
            logger.debug("Doing risk_score: {}, giving lambda: {}".format(risk_score, lam))
            try:
                weights, cost = markowitz_optimizer_3(xs, sigma, lam, mu, constraints)
                if not weights.any():
                    raise Unsatisfiable("Could not find an appropriate allocation for Settings: {}".format(setting))

                # Find the optimal orderable weights.
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
                                               goal_instruments['price'])
                # Convert to our statistics for our portfolio.
                portfolios.append((risk_score,
                                   get_portfolio_stats(goal_instruments,
                                                       goal_symbol_ixs,
                                                       instruments,
                                                       lcovars,
                                                       weights)))
                found = True

            except Unsatisfiable as e:
                logger.debug("No allocation possible for lambda: {}".format(lam))
                last_err = e
                portfolios.append((risk_score, None))

        if not found:
            raise Unsatisfiable("No suitable portfolio could be found for any risk score. Last reason: {}".format(last_err))

    except:
        logger.exception("Problem calculating portfolio for setting: {}".format(setting))
        raise

    return portfolios


class Unsatisfiable(Exception):
    # TODO: Give this more structured data
    pass


def optimize_settings(settings, idata):
    """
    Calculates the portfolio weights
    :param settings:
    :param idata:
    :param single:
    :return:
    """
    # Optimise for the instrument weights given the constraints
    xs, sigma, mu, lam, constraints, settings_instruments, settings_symbol_ixs, instruments, lcovars = calc_opt_inputs(settings, idata)
    logger.debug("Optimising settings using lambda: {}, mu: {}\ncovars: {}\nsigma: {}".format(lam, mu, lcovars, sigma))
    weights, cost = markowitz_optimizer_3(xs, sigma, lam, mu, constraints)

    if not weights.any():
        raise Unsatisfiable("Could not find an appropriate allocation for Settings: {}".format(settings))

    return weights, cost, xs, sigma, mu, lam, constraints, settings_instruments, settings_symbol_ixs, instruments, lcovars


def calc_opt_inputs(settings, idata, metric_overrides=None):
    # Get the global instrument data
    covars, samples, instruments, masks = idata

    # Convert the settings into a constraint based on a mask for the instruments appropriate for the settings given
    settings_symbol_ixs, cvx_masks = get_settings_masks(settings, masks)
    if len(settings_symbol_ixs) == 0:
        raise Unsatisfiable("No assets available for settings: {} given it's constraints.".format(settings))
    xs, constraints = get_core_constraints(len(settings_symbol_ixs))
    lam, mconstraints = get_metric_constraints(settings, cvx_masks, xs, metric_overrides)
    constraints += mconstraints
    logger.debug("Got constraints for settings: {}. Active symbols:{}".format(settings, settings_symbol_ixs))

    settings_instruments = instruments.iloc[settings_symbol_ixs]

    # Get the initial weights for the optimisation using only the target instruments
    market_caps = get_market_caps(settings_instruments)

    # Get the views appropriate for the settings
    views, vers = get_views(settings.goal.portfolio_set, settings_instruments)

    # Pass the data to the BL algorithm to get the the mu and sigma for the optimiser
    lcovars = covars.iloc[settings_symbol_ixs, settings_symbol_ixs]
    mu, sigma = bl_model(lcovars.values,
                         market_caps.values,
                         views,
                         vers,
                         samples)

    return xs, sigma, mu, lam, constraints, settings_instruments, settings_symbol_ixs, instruments, lcovars


def calculate_portfolio(settings, idata=None):
    """
    Calculates the instrument weights to use for a given goal settings.
    :param settings: The settings to calculate the portfolio for.
    :return: (weights, er, variance) All values will be None if no suitable allocation can be found.
             - weights: A Pandas series of weights for each instrument.
             - er: Expected return of portfolio
             - stdev: stdev of portfolio
    """
    if idata is None:
        idata = get_instruments()
    logger.debug("Calculating portfolio for settings: {}".format(settings))

    odata = optimize_settings(settings, idata)
    weights, cost, xs, sigma, mu, lam, constraints, settings_instruments, settings_symbol_ixs, instruments, lcovars = odata

    # Find the optimal orderable weights.
    weights, cost = make_orderable(weights,
                                   cost,
                                   xs,
                                   sigma,
                                   mu,
                                   lam,
                                   constraints,
                                   settings,
                                   # We use the current balance (including pending deposits).
                                   settings.goal.current_balance,
                                   settings_instruments['price'])

    return get_portfolio_stats(settings_instruments, settings_symbol_ixs, instruments, lcovars, weights)


def get_portfolio_stats(settings_instruments, settings_symbol_ixs, instruments, lcovars, weights):
    """

    :param settings_instruments:
    :param settings_symbol_ixs:
    :param instruments:
    :param lcovars:
    :param weights:
    :return: (weights, er, stdev)
            - weights is Pandas series of weights indexed on symbol
            - er is the expected return of the portfolio
            - stdev is the stdev of the portfolio returns
    """
    # Get the totals per asset class, portfolio expected return and portfolio variance
    instruments['_weight_'] = 0.0
    instruments.iloc[settings_symbol_ixs, instruments.columns.get_loc('_weight_')] = weights

    # LOGIC TO RETURN GROUPED BY ASSET CLASS
    # ret_weights = instruments.groupby('ac')['_weight_'].sum()

    # LOGIC TO RETURN PER ASSET ID
    ret_weights = instruments.set_index('id')['_weight_']

    # Filter out assets with no allocation
    ret_weights = ret_weights[ret_weights > 0.01]

    # Generate portfolio variance and expected return
    er = weights.dot(settings_instruments['exp_ret'])
    logger.debug("Generated asset weights: {}".format(weights))
    logger.debug("Generated portfolio expected return of {} using asset returns: {}".format(er, settings_instruments['exp_ret']))
    variance = weights.dot(lcovars).dot(weights.T)
    logger.debug("Generated portfolio variance of {} using asset covars: {}".format(variance, lcovars))

    # Convert variance to stdev
    return ret_weights, er, variance ** (1 / 2)


def current_stats_from_weights(weights):
    """
    :param weights: A list of (ticker_id, weight) tuples.
    :return: (portfolio_er, portfolio_stdev, {ticker_id: ticker_variance})
    """
    covars, samples, instruments, masks = get_instruments()

    ix = instruments.set_index('id').index
    ilocs = []
    res = {}
    wts = []
    for tid, weight in weights:
        iloc = ix.get_loc(tid)
        ilocs.append(iloc)
        res[tid] = covars.iloc[iloc, iloc]
        wts.append(weight)


    # Generate portfolio stdev and expected return
    nweights = np.array(wts)
    lcovars = covars.iloc[ilocs, ilocs]
    lers = instruments['exp_ret'].iloc[ilocs]
    er = nweights.dot(lers)
    logger.debug("Generated portfolio expected return of {} using current asset returns: {}".format(er, lers))
    variance = nweights.dot(lcovars).dot(nweights.T)
    logger.debug("Generated portfolio variance of {} using current asset covars: {}".format(variance, lcovars))

    return er * 100, (variance * 100 * 100) ** (1 / 2), res


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
            raise Unsatisfiable(emsg.format(budget, SYSTEM_CURRENCY, LMT_PORTFOLIO_PCT * 100, math.ceil(req_budget)))

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
        raise Unsatisfiable("Could not find an appropriate allocation given ordering constraints for settings: {} ".format(settings))

    logger.info('Ordering cost for settings {}: {}, pre-ordering val: {}'.format(settings.id,
                                                                                 min_cost - original_cost,
                                                                                 original_cost))

    return wts[0], min_cost


def get_unconstrained(portfolio_set):
    covars, samples, instruments, masks = get_instruments()
    ps_ixs = masks[PORTFOLIO_SET_MASK_PREFIX + str(portfolio_set.id)].nonzero()[0].tolist()
    ps_instrs = instruments.iloc[ps_ixs]
    xs, constraints = get_core_constraints(len(ps_instrs))
    market_caps = get_market_caps(ps_instrs)

    # Get the views appropriate for the portfolio set
    views, vers = get_views(portfolio_set, ps_instrs)

    # Pass the data to the BL algorithm to get the the mu and sigma for the optimiser
    lcovars = covars.iloc[ps_ixs, ps_ixs]
    mu, sigma = bl_model(lcovars.values,
                         market_caps.values,
                         views,
                         vers,
                         samples)
    fid = AssetFeatureValue.objects.get(name='Stocks Only').id
    stocks_mask = masks.iloc[ps_ixs, masks.columns.get_loc(fid)].nonzero()[0].tolist()
    logger.debug("Portfolio Set: {}. Unconstrained symbols: {}, stocks: {}".format(portfolio_set.name,
                                                                                   ps_instrs.index,
                                                                                   stocks_mask))
    json_portfolios = {}
    for allocation in list(np.arange(0, 1.01, 0.01)):
        nc = constraints + [sum_entries(xs[stocks_mask]) == allocation]
        weights, cost = markowitz_optimizer_3(xs, sigma, 1.2, mu, nc)
        if weights.any():
            weights, er, vol = get_portfolio_stats(ps_instrs, ps_ixs, instruments, lcovars, weights)
        else:
            instruments['_weight_'] = 0
            weights = instruments.groupby('ac')['_weight_'].sum()
            weights[:] = 1/len(weights)
            er = 0.0
            vol = 0.0
        json_portfolios["{0:.2f}".format(allocation)] = {
            "allocations": weights.to_dict(),
            "risk": allocation,
            "expectedReturn": er * 100,
            # Vol we return is stddev
            "volatility": (vol * 100 * 100) ** (1 / 2)
        }

    return json_portfolios


def get_all_optimal_portfolios():
    # calculate default portfolio
    api = DbApi()#get_api("YAHOO")

    # calculate portfolios
    for goal in Goal.objects.all():
        if goal.selected_settings is not None:
            try:
                calculate_portfolios(goal.selected_settings, api=api)
            except Unsatisfiable as e:
                logger.warn(e)


class Command(BaseCommand):
    help = 'Calculate all the optimal portfolios for all the goals in the system.'

    def handle(self, *args, **options):
        get_all_optimal_portfolios()
