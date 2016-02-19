from collections import defaultdict
# Use ujson as normal json doesn't support setting float precision
import ujson
import sys
import math
import datetime

from main.management.commands.convert_metrics import convert_goal
from main.models import Ticker, SYSTEM_CURRENCY, AssetFeatureValue, MarkowitzScale, PortfolioSet
from portfolios.BL_model.bl_model import bl_model, markowitz_optimizer_3, markowitz_cost
from portfolios.api.yahoo import DbApi
from portfolios.bl_model import calculate_co_vars
from portfolios.profile_it import do_cprofile
from main.models import Goal
from django.core.management.base import BaseCommand

from cvxpy import sum_entries, Variable
import logging
import pandas as pd
import numpy as np

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
        - N x 4 Instruments table
            - Column 1 (exp_ret): Annualised expected return
            - Column 2 (mkt_cap): Market cap or AUM in system currency
            - Column 3 (ac): The asset class the instrument belongs to.
            - Column 4 (price): The current market midprice
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
                      ac_ps[ticker.asset_class.id]))

    # Filter the table to be only complete.
    ctable = pd.concat(ccols, axis=1).iloc[minix:, :]

    # For some reason once I added the exclude arg below, the index arg was ignored, so I have to do it manually after.
    instruments = pd.DataFrame.from_records(irows,
                                            columns=['symbol', 'exp_ret', 'mkt_cap', 'ac', 'price', 'features', 'pids'],
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
    # TODO: Go to a redis store to get it. If it's not there, add it.
    return build_instruments(api)


def get_goal_masks(goal, masks):
    '''
    :param goal: The goal we want to modify the global masks for
    :param masks: The global asset feature masks
    :return: (goal_symbol_ixs, cvx_masks)
        - goal_symbol_ixs: A list of ilocs into the masks index for the symbols used in this goal.
        - cvx_masks: A dict from mask name to list of indicies in the goal_symbols list that match this mask name.
    '''
    removals = np.array([False] * len(masks))

    # logger.debug("Creating Goal masks from global masks: {}".format(masks))
    fids = []

    for metric in goal.metrics.all():
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
    goal_mask = np.logical_not(removals)
    logger.debug("Goal mask for goal: {} after removals: {} ({} items)".format(goal, goal_mask, len(goal_mask.nonzero())))

    # Only use the instruments from the specified portfolio set.
    goal_mask &= masks[PORTFOLIO_SET_MASK_PREFIX + str(goal.portfolio_set.id)]

    logger.debug("Usable indicies in our portfolio: {}".format(goal_mask.nonzero()[0].tolist()))

    # Convert a global feature masks mask into an index list suitable for the optimisation variables.
    cvx_masks = {fid: masks.loc[goal_mask, fid].nonzero()[0].tolist() for fid in fids}
    logger.debug("CVX masks for goal: {}: {}".format(goal, cvx_masks))

    return goal_mask.nonzero()[0].tolist(), cvx_masks


def get_core_constraints(nvars):
    """
    Creates the core cvxpy constraints and optimisation variables for any portfolio optimisation calculation.
    :param nvars: The number of optimisation variables to create.
    :return: (xs, constraints)
        - xs: The list of cvxpy variables that we will optimise for. Length is count of trues in goal_mask
        - constraints: The core constraints suitable for cvxpy
    """
    # Create the list of variables that we will optimise for.
    xs = Variable(nvars)

    # Start with the constraint that all must add to 1
    constraints = [sum_entries(xs) == 1]

    # Add the constraint that all must be positive
    constraints.append(xs >= 0)

    return xs, constraints


def get_metric_constraints(goal, cvx_masks, xs, overrides=None):
    """
    Adds the constraints to be used by cvxpy coming from the metrics for this goal.
    :param goal: Details of the goal you want the constraints for
    :param cvx_masks: A dict of all the goal-specific cvxpy iloc lists against the goal_symbols for each mask name.
    :param xs: The list of cvxpy variables we are optimising
    :return: (lambda, constraints)
    """
    constraints = []
    risk_score = None
    for metric in goal.metrics.all():
        if metric.type == 1:
            risk_score = metric.configured_val
        elif metric.type == 0:  # Portfolio Mix
            if overrides:
                val = overrides.get(metric.feature.id, metric.configured_val)
            # Non-inclusions are taken care of in the goal mask, so ignore those constraints.
            if math.isclose(val, 0.0):
                continue
            # Saying a maximum percentage of 100% is superfluous, so ignore those constraints.
            if math.isclose(val, 1.0) and metric.comparison == 2:
                continue

            feature_assets = cvx_masks[metric.feature.id]
            # If we have no possible symbols, and we have a metric with a non-zero allocation, fail.
            if len(feature_assets) == 0 and metric.comparison != 2:
                raise Unsatisfiable("Goal metric: {} is not satisfiable.".format(metric))
            if metric.comparison == 0:
                logger.debug("Adding constraint that goal symbols: {} must be minimum {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) >= val)
            elif metric.comparison == 1:
                logger.debug("Adding constraint that goal symbols: {} must be exactly {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) == val)
            elif metric.comparison == 2:
                logger.debug("Adding constraint that goal symbols: {} must be maximum {}".format(feature_assets, val))
                constraints.append(sum_entries(xs[feature_assets]) <= val)
            else:
                raise Exception("Unknown metric comparison value: {} found for goal: {}".format(metric.comparison, goal))
        else:
            raise Exception("Unknown metric type: {} found for goal: {}".format(metric.type, goal))

    if risk_score is None:
        raise Exception("Risk score metric could not be found for goal: {}".format(goal))

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
    :param instruments: The instruments table for this goal
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
def calculate_portfolios(goal, api=DbApi()) -> str:
    logger.debug("Calculate Portfolios Requested")
    try:
        idata = get_instruments(api)
        convert_goal(goal)
        logger.debug("Got instruments")
        json_portfolios = {}
        # TODO: Range over lambda, not stocks alloc.
        oldalloc = goal.allocation
        stocks_feat = AssetFeatureValue.objects.get(name='Stocks Only').id
        for allocation in list(np.arange(0, 1.01, 0.01)):
            logger.debug("Doing alloc: {}".format(allocation))
            # TODO: Remove this hack and actually continue the exception to JSON side
            try:
                # Calculate the opt inputs for ranging alloc
                ovr = {stocks_feat: allocation}
                xs, sigma, mu, lam, constraints, goal_instruments, goal_symbol_ixs, instruments, lcovars = calc_opt_inputs(goal, idata, metric_overrides=ovr)
                logger.debug("Optimising goal using lambda: {}, mu: {}\ncovars: {}\nsigma: {}".format(lam, mu, lcovars, sigma))
                weights, cost = markowitz_optimizer_3(xs, sigma, lam, mu, constraints)

                if not weights.any():
                    raise Unsatisfiable("Could not find an appropriate allocation for Goal: {}".format(goal))

                # Find the optimal orderable weights.
                weights, cost = make_orderable(weights, cost, xs, sigma, mu, lam, constraints, goal, goal_instruments['price'])

                weights, er, vol = get_portfolio_stats(goal_instruments, goal_symbol_ixs, instruments, lcovars, weights)
            except Unsatisfiable as e:
                logger.warn(e)
                idata[2]['_weight_'] = 0
                weights = idata[2].groupby('ac')['_weight_'].sum()
                # We set all the weights even, but still adding to 1, as the UI can't handle otherwise.
                weights[:] = 1/len(weights)
                er = 0.0
                vol = 0.0

            if weights is not None:
                json_portfolios["{0:.2f}".format(allocation)] = {
                    "allocations": weights.to_dict(),
                    "risk": allocation,
                    "expectedReturn": er * 100,
                    # Vol we return is stddev
                    "volatility": (vol * 100 * 100) ** (1 / 2)
                }
        goal.allocation = oldalloc
    except:
        logger.exception("Problem calculating portfolio for goal: {}".format(goal))
        raise

    return json_portfolios


class Unsatisfiable(Exception):
    pass


def optimize_goal(goal, idata):
    """
    Calculates the goal weights
    :param goal:
    :param idata:
    :param single:
    :return:
    """
    # Optimise for the instrument weights given the constraints
    xs, sigma, mu, lam, constraints, goal_instruments, goal_symbol_ixs, instruments, lcovars = calc_opt_inputs(goal, idata)
    logger.debug("Optimising goal using lambda: {}, mu: {}\ncovars: {}\nsigma: {}".format(lam, mu, lcovars, sigma))
    weights, cost = markowitz_optimizer_3(xs, sigma, lam, mu, constraints)

    if not weights.any():
        raise Unsatisfiable("Could not find an appropriate allocation for Goal: {}".format(goal))

    return weights, cost, xs, sigma, mu, lam, constraints, goal_instruments, goal_symbol_ixs, instruments, lcovars


def calc_opt_inputs(goal, idata, metric_overrides=None):
    # Get the global instrument data
    covars, samples, instruments, masks = idata

    # Convert the goal into a constraint based on a mask for the instruments appropriate for the goal given
    goal_symbol_ixs, cvx_masks = get_goal_masks(goal, masks)
    if len(goal_symbol_ixs) == 0:
        raise Unsatisfiable("No assets available for goal: {} given it's constraints.".format(goal))
    xs, constraints = get_core_constraints(len(goal_symbol_ixs))
    lam, mconstraints = get_metric_constraints(goal, cvx_masks, xs, metric_overrides)
    constraints += mconstraints
    logger.debug("Got constraints for goal: {}. Active symbols:{}".format(goal, goal_symbol_ixs))

    goal_instruments = instruments.iloc[goal_symbol_ixs]

    # Get the initial weights for the optimisation using only the target instruments
    market_caps = get_market_caps(goal_instruments)

    # Get the views appropriate for the goal
    views, vers = get_views(goal.portfolio_set, goal_instruments)

    # Pass the data to the BL algorithm to get the the mu and sigma for the optimiser
    lcovars = covars.iloc[goal_symbol_ixs, goal_symbol_ixs]
    mu, sigma = bl_model(lcovars.values,
                         market_caps.values,
                         views,
                         vers,
                         samples)

    return xs, sigma, mu, lam, constraints, goal_instruments, goal_symbol_ixs, instruments, lcovars


def calculate_portfolio(goal, idata):
    """
    Calculates the instrument weights to use for a given goal.
    :param goal: The goal to calculate the portflio for.
    :return: (ac_weights, er, variance) All values will be None if no suitable allocation can be found.
             - ac_weights: A Pandas series of weights for each instrument asset class.
             - er: Expected return of portfolio
             - variance: Total variance of portfolio
    """
    logger.debug("Calculating portfolio for alloc: {}".format(goal.allocation))

    weights, cost, xs, sigma, mu, lam, constraints, goal_instruments, goal_symbol_ixs, instruments, lcovars = optimize_goal(goal, idata)

    # Find the optimal orderable weights.
    weights, cost = make_orderable(weights, cost, xs, sigma, mu, lam, constraints, goal, goal_instruments['price'])

    return get_portfolio_stats(goal_instruments, goal_symbol_ixs, instruments, lcovars, weights)


def get_portfolio_stats(goal_instruments, goal_symbol_ixs, instruments, lcovars, weights):
    # Get the totals per asset class, portfolio expected return and portfolio variance
    instruments['_weight_'] = 0.0
    instruments.iloc[goal_symbol_ixs, instruments.columns.get_loc('_weight_')] = weights
    ac_weights = instruments.groupby('ac')['_weight_'].sum()
    # TODO: Remove this "return everything" functionality to only return asset classes with an allocation.
    # ac_weights = ac_weights[ac_weights > 0.01]
    # TODO: Should we really be displaying the expected return from the time series, or the BL mu?
    er = weights.dot(goal_instruments['exp_ret'])
    logger.debug("Generated asset weights: {}".format(weights))
    logger.debug("Generated portfolio expected return of {} using asset returns: {}".format(er, goal_instruments['exp_ret']))
    variance = weights.dot(lcovars).dot(weights.T)
    logger.debug("Generated portfolio variance of {} using asset covars: {}".format(variance, lcovars))
    return ac_weights, er, variance


def make_orderable(weights, original_cost, xs, sigma, mu, lam, constraints, goal, prices):
    """
    Turn the raw weights into orderable units
    There are three costs here:
    - Markowitz cost
    - Variation from budget
    - Variation from constraints
    For now we just minimize the Markowitz cost, but we can be smarter.

    :param weights: A 1xn numpy array of the weights we need to perturbate to fit into orderable units.
    :param original_cost: The pre-ordering Markowitz cost
    :param xs: The cvxpy variables (length n) we can feed to the optimizer
    :param sigma: A nxn numpy array of the covariances matrix between assets
    :param mu: A 1xn numpy array of the expected returns per asset
    :param lam: The Markowitz risk appetite constant
    :param constraints: The existing constraints we must adhere to
    :param goal: The goal we are making this portfolio orderable for.
    :param prices: The prices of each asset.
    :return: (weights, cost)
        - weights are the new symbol weights that should align to orderable units given the passed prices.
          This will be an empty array if no orderable portfolio could be found.
        - cost is the new Markowitz cost
    """
    budget = goal.total_balance + goal.cash_balance + goal.pending_deposits + goal.pending_withdrawals

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
        # TODO: Figure out the ordering costs of the assets for this customer at this point based on currrent holdings,
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
            emsg = "Could not find orderable portfolio for goal: {} once I removed assets below ordering threshold"
            raise Unsatisfiable(emsg.format(goal))

    # Create a collection of all instruments that are to be included, but the weights are currently not on an orderable
    # quantity.
    # Find the minimum Markowitz cost off all the potential portfolio combinations that could be generated from a round
    # up and round down of each fund involved to orderable quantities.
    # TODO: We could also weight results with distance of portfolio from the budget.
    indicies = []
    tweights = []
    for ix in range(len(weights)):
        if inactive[ix] or aligned(ix):
            continue
        indicies.append(ix)
        tweights.append(bordering(ix))

    elems = len(indicies)
    wts = np.expand_dims(weights, axis=0)
    if elems > 0:
        rounds = 2 ** elems
        min_cost = sys.float_info.max
        # TODO: This could be done parallel
        for mask in range(rounds):
            # Set the weights for this round
            for pos, tweight in enumerate(tweights):
                wts[0, indicies[pos]] = tweight[(mask & (1 << pos)) > 0]
            new_cost = markowitz_cost(wts, sigma, lam, mu)
            if new_cost < min_cost:
                mcw = np.copy(wts)
                min_cost = new_cost
        wts = mcw

    if not wts.any():
        raise Unsatisfiable("Could not find an appropriate allocation given ordering constraints for goal: {} ".format(goal))

    logger.info('Ordering cost for goal {}: {}, pre-ordering val: {}'.format(goal.id,
                                                                             min_cost-original_cost,
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
    yahoo_api = DbApi()#get_api("YAHOO")

    for ps in PortfolioSet.objects.all():
        ps.portfolios = ujson.dumps(get_unconstrained(ps), double_precision=2)
        ps.save()

    # calculate portfolios
    for goal in Goal.objects.all():
        if goal.is_custom_size:
            try:
                ports = calculate_portfolios(goal, api=yahoo_api)
                goal.portfolios = ujson.dumps(ports, double_precision=2)
            except Unsatisfiable as e:
                logger.warn(e)
                goal.portfolios = '{}'
            goal.save()


class Command(BaseCommand):
    help = 'Calculate all the optimal portfolios for all the goals in the system.'

    def handle(self, *args, **options):
        get_all_optimal_portfolios()
