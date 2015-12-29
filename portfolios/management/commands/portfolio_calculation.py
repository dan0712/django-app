from main.models import Ticker, Region, INVESTMENT_TYPES, STOCKS
from portfolios.BL_model.bl_model import bl_model, markowitz_optimizer_3
from portfolios.api.yahoo import DbApi
from portfolios.bl_model import calculate_co_vars
from portfolios.profile_it import do_cprofile
from ...models import PortfolioSet
from main.models import Goal
from django.core.management.base import BaseCommand

from cvxpy import sum_entries, Variable
import logging
import pandas as pd
import numpy as np
import traceback
import json

TYPE_MASK_PREFIX = 'TYPE_'
ETHICAL_MASK_NAME = 'ETHICAL'
REGION_MASK_PREFIX = 'REGION_'
ETF_MASK_NAME = 'ETF'

logger = logging.getLogger('betasmartz.portfolio_calculation')
#logger.setLevel(logging.DEBUG)


def build_instruments(api=DbApi()):
    """
    Builds all the instruments know about in the system.
    Have global pandas tables of all the N instruments in the system, and operate on these tables through masks.
        - N x 2 Instruments table. Column 1 is Annualised expected return, 2 is market cap in AUD
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
    tickers = Ticker.objects.all()
    # Much faster building the dataframes once, not appending on iteration.
    irows = []
    ccols = []
    num_prices = None
    for ticker in tickers:
        prices = api.get_all_prices(ticker.symbol, currency=ticker.currency).dropna()
        if num_prices is None:
            num_prices = len(prices)
        elif num_prices != len(prices):
            # TODO: Put the warning back
            #logger.warn("All prices not the same for all instruments. Last len: {}, Prices: {}".format(num_prices, prices))
            # raise Exception("All prices not available for all instruments.")
            pass
        ccols.append(prices)
        # Build annualised expected return
        er = (1 + ccols[-1].pct_change().mean()) ** 12 - 1
        irows.append((ticker.symbol,
                      er,
                      api.market_cap(ticker),
                      ticker.region.id,
                      ticker.ethical,
                      ticker.etf,
                      ticker.asset_class.investment_type))
    ctable = pd.concat(ccols, axis=1)
    instruments = pd.DataFrame.from_records(irows,
                                            columns=['symbol', 'exp_ret', 'mkt_cap', 'reg', 'eth', 'etf', 'type'],
                                            index=['symbol'])
    masks = pd.DataFrame(index=instruments.index)
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

    #sk_co_var, co_vars = calculate_co_vars(ctable.shape[1], ctable)
    #co_vars = pd.DataFrame(co_vars, index=instruments.index, columns=instruments.index)
    
    # Drop dates that have nulls for some symbols.
    # TODO: Have some sanity check over the data. Make sure it's recent, gap free and with enough samples.
    co_vars = ctable.dropna().cov()

    logger.debug("Prices table: {}".format(ctable.values.tolist()))

    # TODO: This number of samples is not equal for all instruments
    return co_vars, ctable.dropna().shape[0], instruments, masks


def get_instruments(api=DbApi()):
    # TODO: Go to a redis store to get it. If it's not there, add it.
    return build_instruments(api)


def get_goal_mask(goal, masks):
    goal_mask = pd.DataFrame([False] * len(masks), index=masks.index)
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
        goal_mask[0] |= masks[mask_name]

    if "_ETHICAL" in goal.type:
        goal_mask[0] &= masks[ETHICAL_MASK_NAME]

    return goal_mask


def get_cvx_constraints(goal, masks):
    """
    Gets the allocation constraints to be used by cvxpy that are appropriate for this goal.
    :param goal: Details of the goal you want the constraints for
    :param masks: A pandas dataframe of all the masks available in the system. Indexed on symbol.
    :return: (xs, goal_mask, constraints)
        - xs: The list of cvxpy variables that we will optimise for. Length is count of trues in goal_mask
        - goal_mask: The mask (pandas boolean dataframe indexed on symbol) of the symbols appropriate for this goal
        - constraints: The constraints suitable for cvxpy
    """
    constraints = []

    goal_mask = get_goal_mask(goal, masks)

    # Convert a global masks mask into an index list suitable for the optimisation variables.
    def var_list(mname):
        return masks[mname][goal_mask[0]].values.nonzero()[0].tolist()

    # Create the list of variables that we will optimise for.
    xs = Variable(len(masks[goal_mask[0]]))

    # TODO: Only use the instruments from the specified portfolio set.

    # If optimisation mode is 1, use the picked_regions, otherwise, use the region_sizes
    if goal.optimization_mode == 2:
        for region, sz in goal.region_sizes.items():
            # TODO make the constraint lookup on primary key, not name
            var_lst = var_list(REGION_MASK_PREFIX + str(Region.objects.get(name=region).id))
            if not var_lst:
                raise Exception("No instruments applicable for region constraint. Region: {}, Goal: {}".format(region, goal.name))
            constraints.append(sum_entries(xs[var_lst]) == sz)

    # Add the constraint for allocation
    var_lst = var_list(TYPE_MASK_PREFIX + STOCKS)
    if var_lst:
        constraints.append(sum_entries(xs[var_lst]) == goal.allocation)
    elif goal.allocation > 0:
        raise Exception("No instruments applicable for allocation constraint. Allocation: {}, Goal: {}".format(goal.allocation, goal.name))

    # Add the constraint for satAlloc
    var_lst = var_list(ETF_MASK_NAME)
    if var_lst:
        constraints.append(sum_entries(xs[var_lst]) == 1-goal.satellite_pct)
    elif 1-goal.satellite_pct > 0:
        raise Exception("No instruments applicable for Core percent constraint. Required Core pct: {}, Goal: {}".format(1-goal.satellite_pct, goal.name))

    # Add the constraint that all must add to 1
    constraints.append(sum_entries(xs) == 1)

    # Add the constraint that all must be positive
    constraints.append(xs >= 0)

    # TODO Make the ethical constraint just another constraint on instruments from the UI, not a feature of the goal.
    if "_ETHICAL" in goal.type:
        constraints.append(sum_entries(xs[var_list(ETHICAL_MASK_NAME)]) == 1)

    # TODO: If we're not aggregating orders, add constraints for ordering sizes
    # - i.e. we cannot order 1.2 of an instrument.

    return xs, goal_mask, constraints


def get_initial_weights(instruments):
    """
    Get a set of initial weights based on relative market capitalisation
    :param instruments: The master instruments table
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
            er = None if er is None else float("{0:.4f}".format(er)) * 100
            var = None if var is None else float("{0:.4f}".format((var * 100 * 100) ** (1 / 2)))

            json_portfolios["{0:.2f}".format(allocation)] = {
                "allocations": weights.to_dict(),
                "risk": allocation,
                "expectedReturn": er,
                "volatility": var
            }
        goal.allocation = oldalloc
    except:
        logger.exception("Problem calculating portfolio for goal: {}".format(goal))
        raise

    return json_portfolios


def calculate_portfolio(goal, idata):
    """
    Calculates the instrument weights to use for a given goal.
    :param goal:
    :return: Pandas series of weights for each instrument.
    """
    logger.debug("Calculating portfolio for alloc: {}".format(goal.allocation))

    # Get the global instrument data
    covars, samples, instruments, masks = idata

    # Convert the goal into a constraint based on a mask for the instruments appropriate for the goal given
    xs, goal_mask, constraints = get_cvx_constraints(goal, masks)
    logger.debug("Got constraints")

    # Get the initial weights for the optimisation using only the target instruments
    initial_weights = get_initial_weights(instruments[goal_mask[0]])

    # Get the views appropriate for the goal
    views, vers = get_views(goal, instruments[goal_mask[0]])

    # Pass the data to the BL algorithm to get the the mu and sigma for the optimiser
    lcovars = covars.loc[goal_mask[0], goal_mask[0]]
    mu, sigma = bl_model(lcovars.values,
                         initial_weights[goal_mask[0]].values,
                         views,
                         vers,
                         samples)
    logger.debug("Got mu: {}, covars: {} and sigma: {}".format(mu, lcovars, sigma))

    # Optimise for the instrument weights given the constraints
    weights = markowitz_optimizer_3(xs, sigma, 1, mu, constraints)

    if len(weights) == 1 and weights[0] is None:
        logger.debug("Could not find an appropriate allocation for Goal: {}".format(goal))
        er = None
        variance = None
    else:
        # Remove any weights below the threshold and re-optimize
        '''
        low_mask = weights < 0.02
        logger.debug("Low_mask = {}".format(low_mask))
        low_ixs = low_mask.nonzero()[0].tolist()
        logger.debug("Low_ixs = {}".format(low_ixs))
        constr = xs[low_ixs] == 0
        logger.debug("Constraint = {}".format(constr))
        weights = markowitz_optimizer_3(xs, sigma, 1, mu, constraints.append(constr))
        logger.debug("New Weights = {}".format(weights))  
        '''
        # Get the portfolio expected return and variance
        er = weights.dot(instruments['exp_ret'][goal_mask[0]])
        variance = weights.dot(lcovars).dot(weights)

    retser = pd.Series(weights, index=instruments[goal_mask[0]].index).reindex(instruments.index, fill_value=0)

    # TODO Remove this portfolio mask once the UI handles missing symbols
    #portfolio_symbols = set()
    #for cls in goal.portfolio_set.asset_classes.all():
    #    for ticker in cls.tickers.all():
    #        portfolio_symbols.add(ticker.symbol)
    #portfolio_mask = [item in portfolio_symbols for item in instruments.index]
    #retser = retser[portfolio_mask

    return retser, er, variance


def get_all_optimal_portfolios():
    # calculate default portfolio
    yahoo_api = DbApi()#get_api("YAHOO")

    for ps in PortfolioSet.objects.all():
        goal = Goal()
        goal.custom_portfolio_set = ps
        ps.portfolios = json.dumps(calculate_portfolios(goal, api=yahoo_api))
        ps.save()

    # calculate portfolios
    for goal in Goal.objects.all():
        if goal.is_custom_size:
            goal.portfolios = json.dumps(calculate_portfolios(goal, api=yahoo_api))
            goal.save()


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        get_all_optimal_portfolios()
