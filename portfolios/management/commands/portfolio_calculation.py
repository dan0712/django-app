from collections import defaultdict
# Use ujson as normal json doesn't support setting float precision
import ujson

from main.models import Ticker, Region, INVESTMENT_TYPES, STOCKS
from portfolios.BL_model.bl_model import bl_model, markowitz_optimizer_3
from portfolios.api.yahoo import DbApi
from portfolios.bl_model import calculate_co_vars
from portfolios.management.commands.calculate_portfolios import calculate_portfolios_for_goal
from portfolios.profile_it import do_cprofile
from ...models import PortfolioSet
from main.models import Goal
from django.core.management.base import BaseCommand

from cvxpy import sum_entries, Variable
import logging
import pandas as pd
import numpy as np
import json


TYPE_MASK_PREFIX = 'TYPE_'
ETHICAL_MASK_NAME = 'ETHICAL'
REGION_MASK_PREFIX = 'REGION_'
PORTFOLIO_SET_MASK_PREFIX = 'PORTFOLIO-SET_'
ETF_MASK_NAME = 'ETF'

logger = logging.getLogger('betasmartz.portfolio_calculation')
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

# Raise exceptions if we're doing something dumb with pandas slices
pd.set_option('mode.chained_assignment', 'raise')


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
    num_prices = None
    for ticker in tickers:
        # TODO: Get the current price from the daily prices table, not monthly.
        prices = api.get_all_prices(ticker.symbol, currency=ticker.currency).dropna()
        if num_prices is None:
            num_prices = prices.size
        elif num_prices != prices.size:
            # TODO: Put the warning back
            #logger.warn("All prices not the same for all instruments. Last len: {}, Prices: {}".format(num_prices, prices))
            # raise Exception("All prices not available for all instruments.")
            pass
        if prices.size < 5:
            emsg = "Symbol: {} has only {} available prices. Removing from candidates."
            logger.warn(emsg.format(ticker.symbol, prices.size))
            continue
        ccols.append(prices)
        # Build annualised expected return
        er = (1 + ccols[-1].pct_change().mean()) ** 12 - 1
        irows.append((ticker.symbol,
                      er,
                      api.market_cap(ticker),
                      ticker.region.id,
                      ticker.ethical,
                      ticker.etf,
                      ticker.asset_class.name,
                      prices.iloc[-1],
                      ticker.asset_class.investment_type,
                      ac_ps[ticker.asset_class.id]))

    ctable = pd.concat(ccols, axis=1)
    # For some reason once I added the exclude arg below, the index arg was ignored, so I have to do it manually after.
    instruments = pd.DataFrame.from_records(irows,
                                            columns=['symbol', 'exp_ret', 'mkt_cap', 'reg', 'eth', 'etf', 'ac', 'price', 'type', 'pids'],
                                            exclude=['pids']).set_index('symbol')

    masks = pd.DataFrame(index=instruments.index)

    # Add this symbol to the appropriate portfolio set masks
    psid_miloc = {}
    for psid in PortfolioSet.objects.values_list('id', flat=True):
        mid = PORTFOLIO_SET_MASK_PREFIX + str(psid)
        masks[mid] = False
        psid_miloc[psid] = masks.columns.get_loc(mid)
    for ix, row in enumerate(irows):
        for psid in row[9]:
            masks.iloc[ix, psid_miloc[psid]] = True

    # Build the region masks
    for rid in Region.objects.values_list('id', flat=True):
        masks[REGION_MASK_PREFIX + str(rid)] = instruments['reg'] == rid

    # Build the ethical mask
    masks[ETHICAL_MASK_NAME] = instruments['eth'] == True

    # Build the ETF mask
    masks[ETF_MASK_NAME] = instruments['etf'] == True

    # Build the type masks
    for itype in INVESTMENT_TYPES:
        masks[TYPE_MASK_PREFIX + itype[0]] = instruments['type'] == itype[0]

    # Drop the items from the instruments table that were just used to build the masks.
    instruments.drop(['reg', 'eth', 'type', 'etf'], axis=1, inplace=True)

    # Old covariance
    sk_co_var, co_vars = calculate_co_vars(ctable.shape[1], ctable)
    co_vars = pd.DataFrame(co_vars, index=instruments.index, columns=instruments.index)
    samples = 6
    
    # Drop dates that have nulls for some symbols.
    # TODO: Have some sanity check over the data. Make sure it's recent, gap free and with enough samples.
    #ptable = ctable.dropna()

    #logger.debug("Prices as table: {}".format(ptable.to_dict('list')))
    #logger.debug("Prices as list: {}".format(ptable.values.tolist()))

    #co_vars = ptable.cov()
    #samples = ptable.shape[0]
    return co_vars, samples, instruments, masks


def get_instruments(api=DbApi()):
    # TODO: Go to a redis store to get it. If it's not there, add it.
    return build_instruments(api)


def get_goal_masks(goal, masks):
    '''
    :param goal: The goal we want to modify the global masks for
    :param masks: The global group masks
    :return: (goal_symbol_ixs, cvx_masks)
        - goal_symbol_ixs: A list of ilocs into the masks index for the symbols used in this goal.
        - cvx_masks: A dict from mask name to list of indicies in the goal_symbols list that match this mask name.
    '''
    goal_mask = np.array([False] * len(masks))
    if goal.optimization_mode == 1:
        # TODO: This json should go. We should simply get the region (min,max) percentage constraints from the model
        region_coll = json.loads(goal.picked_regions)
    else:
        assert goal.optimization_mode == 2
        region_coll = goal.region_sizes.keys()

    for region in region_coll:
        # TODO make the constraint lookup on primary key, not name
        logger.debug("Adding region: {} to usable masks".format(region))
        mask_name = REGION_MASK_PREFIX + str(Region.objects.get(name=region).id)
        goal_mask |= masks[mask_name]

    if "_ETHICAL" in goal.type:
        goal_mask &= masks[ETHICAL_MASK_NAME]

    # Only use the instruments from the specified portfolio set.
    goal_mask &= masks[PORTFOLIO_SET_MASK_PREFIX + str(goal.portfolio_set_id)]

    # Convert a global masks mask into an index list suitable for the optimisation variables.
    cvx_masks = {name: masks[name][goal_mask].nonzero()[0].tolist() for name in masks}

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


def get_allocation_constraints(goal, cvx_masks, xs, slippage=0):
    """
    Adds the allocation constraints to be used by cvxpy coming from the allocation percentages for this goal.
    :param goal: Details of the goal you want the constraints for
    :param cvx_masks: A dict of all the goal-specific cvxpy iloc lists against the goal_symbols for each mask name.
    :param xs: The list of cvxpy variables we are optimising
    :param slippage: The allowable slippage from any percentage allocation targets given. 0.1 = 10% slippage from target
                     meaning if the allocation target is 20%, acceptable allocation is 18-22%.
    :return: A List of constraints
    """

    constraints = []

    def add_constraint(ixs, v):
        if slippage:
            constraints.append(sum_entries(xs[ixs]) >= (v - slippage*v))
            constraints.append(sum_entries(xs[ixs]) <= (v + slippage*v))
        else:
            constraints.append(sum_entries(xs[ixs]) == v)

    # If optimisation mode is 1, use the picked_regions, otherwise, use the region_sizes
    if goal.optimization_mode == 2:
        for region, sz in goal.region_sizes.items():
            # TODO make the constraint lookup on primary key, not name
            var_lst = cvx_masks[REGION_MASK_PREFIX + str(Region.objects.get(name=region).id)]
            if not var_lst:
                estr = "No instruments applicable for region constraint. Region: {}, Goal: {}"
                raise Exception(estr.format(region, goal.name))
            add_constraint(var_lst, sz)

    # Add the constraint for allocation
    var_lst = cvx_masks[TYPE_MASK_PREFIX + STOCKS]
    if var_lst:
        add_constraint(var_lst, goal.allocation)
    elif goal.allocation > 0:
        estr = "No instruments applicable for allocation constraint. Allocation: {}, Goal: {}"
        raise Exception(estr.format(goal.allocation, goal.name))

    # Add the constraint for satAlloc
    var_lst = cvx_masks[ETF_MASK_NAME]
    etf_pct = 1-goal.satellite_pct
    if var_lst:
        add_constraint(var_lst, etf_pct)
    elif etf_pct > 0:
        estr = "No instruments applicable for Core percent constraint. Required Core pct: {}, Goal: {}"
        raise Exception(estr.format(etf_pct, goal.name))

    return constraints


def get_ordering_constraint(xs, instruments):
    """
    Adds the allocation constraints to be used by cvxpy coming from the allocation percentages for this goal.
    :param goal: Details of the goal you want the constraints for
    :param masks: A pandas dataframe of all the goal-specific masks for each group in the system. Indexed on symbol.
    :param xs: The list of cvxpy variables we are optimising
    :param instruments: A Pandas DataFrame with all the instrument data.
    :return: A List of constraints
        - xs: The list of cvxpy variables that we will optimise for. Length is count of trues in goal_mask
        - constraints: The constraints suitable for cvxpy
    """
    # TODO: If we're not aggregating orders, or in the US where we can order partials, add constraints for ordering sizes
    # - i.e. we cannot order 1.2 of an instrument. This doesn't work as % is not supported by cvx
    return [xs % 0.01 == 0]


def get_initial_weights(instruments):
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


def get_views(goal, instruments):
    """
    Return the views that are appropriate for a given goal.
    :param goal: The goal to get the views for.
    :param instruments: The n x d pandas dataframe with n instruments and their d data columns.
    :return: (views, view_rets)
        - views is a masked nxm numpy array corresponding to m investor views on future asset movements
        - view_rets is a mx1 numpy array of expected returns corresponding to views.
    """
    # TODO: We should get the cached views per portfolio set from redis
    goal_views = goal.portfolio_set.views.all()
    views = np.zeros((len(goal_views), instruments.shape[0]))
    qs = []
    masked_views = []
    for vi, view in enumerate(goal_views):
        header, view_values = view.assets.splitlines()

        header = header.split(",")
        view_values = view_values.split(",")

        for sym, val in zip(header, view_values):
            _symbol = sym.strip()
            try:
                si = instruments.index.get_loc(_symbol)
                views[vi][si] = float(val)
            except KeyError:
                mstr = "Ignoring view: {} in portfolio set: {} for goal: {} as symbol: {} is not active for this goal"
                logger.debug(mstr.format(vi, goal.portfolio_set.name, goal.name, _symbol))
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
        logger.debug("Got instruments")
        json_portfolios = {}
        oldalloc = goal.allocation
        for allocation in list(np.arange(0, 1.01, 0.01)):
            goal.allocation = allocation
            logger.debug("Doing alloc: {}".format(allocation))
            weights, er, var = calculate_portfolio(goal, idata)
            if weights is not None:
                json_portfolios["{0:.2f}".format(allocation)] = {
                    "allocations": weights.to_dict(),
                    "risk": allocation,
                    "expectedReturn": er * 100,
                    "volatility": (var * 100 * 100) ** (1 / 2)
                }
        goal.allocation = oldalloc
    except:
        logger.exception("Problem calculating portfolio for goal: {}".format(goal))
        raise

    return json_portfolios


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

    # Get the global instrument data
    covars, samples, instruments, masks = idata

    # Convert the goal into a constraint based on a mask for the instruments appropriate for the goal given
    goal_symbol_ixs, cvx_masks = get_goal_masks(goal, masks)
    xs, constraints = get_core_constraints(len(goal_symbol_ixs))
    constraints += get_allocation_constraints(goal, cvx_masks, xs)
    # The ethical constraint is represented in the goal_mask, as only ethical instruments will be selected, so we don't
    # have ethical constraints to add.
    logger.debug("Got constraints")

    goal_instruments = instruments.iloc[goal_symbol_ixs]

    # Get the initial weights for the optimisation using only the target instruments
    initial_weights = get_initial_weights(goal_instruments)

    # Get the views appropriate for the goal
    views, vers = get_views(goal, goal_instruments)

    # Pass the data to the BL algorithm to get the the mu and sigma for the optimiser
    lcovars = covars.iloc[goal_symbol_ixs, goal_symbol_ixs]
    mu, sigma = bl_model(lcovars.values,
                         initial_weights.values,
                         views,
                         vers,
                         samples)
    logger.debug("Got mu: {}, covars: {} and sigma: {}".format(mu, lcovars, sigma))

    # Optimise for the instrument weights given the constraints
    weights, cost = markowitz_optimizer_3(xs, sigma, 1, mu, constraints)

    if not weights.any():
        logger.info("Could not find an appropriate allocation for Goal: {}".format(goal))
        return None, None, None
    else:
        # Deactivate any instruments that didn't reach at least orderable quantity of 1 and rerun the optimisation.
        inactive = ((weights[0] * goal.total_balance) / goal_instruments['price']) < 1
        inactive |= weights[0] < .01  # We only return things over 2 dec pl as we round to that in the portfolio.
        inactive_ilocs = inactive.nonzero()[0].tolist()
        if len(inactive_ilocs) > 0:
            constraints.append(xs[inactive_ilocs] == 0)

            # Optimise again given the new constraints
            original_cost = cost
            original_weights = weights
            weights, cost = markowitz_optimizer_3(xs, sigma, 1, mu, constraints)
            if not weights.any():
                logger.info("Could not find an appropriate allocation given ordering constraints for goal: {} ".format(goal))
                logger.info("Reinstating old portfolio for now")
                weights = original_weights
                #return None, None, None
            else:
                logger.info('Ordering cost for goal {}: {}, pre-ordering val: {}'.format(goal.id, cost-original_cost, original_cost))

    # TODO: Now round each allocation to both the above and below unit, and optimise across all combinations to
    # TODO: find the best allocation in terms of cost, slippage from desired constraints, and cost delta vs portfolio
    # TODO: balance.

    # Get the totals per asset class, portfolio expected return and portfolio variance
    instruments['_weight_'] = 0.0
    instruments.iloc[goal_symbol_ixs, instruments.columns.get_loc('_weight_')] = weights[0]
    ac_weights = instruments.groupby('ac')['_weight_'].sum()
    # TODO: Remove this "return everything" functionality to only return asset classes with an allocation.
    #ac_weights = ac_weights[ac_weights > 0.01]
    er = weights.dot(goal_instruments['exp_ret'])
    variance = weights.dot(lcovars).dot(weights.T)

    return ac_weights, er[0], variance[0][0]


def get_all_optimal_portfolios():
    # calculate default portfolio
    yahoo_api = DbApi()#get_api("YAHOO")

    for ps in PortfolioSet.objects.all():
        goal = Goal()
        goal.custom_portfolio_set = ps
        # TODO: Remove this dependency on the old code and build the goal manually here.
        ps.portfolios = ujson.dumps(calculate_portfolios_for_goal(goal, api=yahoo_api), double_precision=2)
        ps.save()

    # calculate portfolios
    for goal in Goal.objects.all():
        if goal.is_custom_size:
            ports = calculate_portfolios(goal, api=yahoo_api)
            goal.portfolios = ujson.dumps(ports, double_precision=2)
            goal.save()


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        get_all_optimal_portfolios()
