'''
Deciding when to rebalance:
 - A user can decide to "Rebalance Now". If the "Rebalance now" button is pressed. Make sure we display to the user
   what the estimated cost of the rebalance is and how it compares to the ATCS.
'''
import copy
import logging

import numpy as np

from main.models import Position, ExecutionRequest, Ticker, MarketOrderRequest, Execution
from portfolios.BL_model.bl_model import markowitz_optimizer_3
from portfolios.management.commands.portfolio_calculation import optimize_settings, make_orderable, MIN_PORTFOLIO_PCT, \
    calc_opt_inputs


logger = logging.getLogger('rebalance')


def optimise_up(opt_inputs, min_weights):
    """
    Reoptimise the portfolio adding appropriate constraints so there can be no removals from assets.
    :param opt_inputs: The basic optimisation inputs for this goal.
    :param min_weights: A dict from asset_id to new minimum weight.
    :return: weights - The new dict of weights, or None if impossible.
    """
    xs, sigma, mu, lam, constraints, settings_instruments, settings_symbol_ixs, instruments, lcovars = opt_inputs
    pweights = np.array([min_weights[tid] for tid in settings_instruments['id'].values])
    new_cons = constraints + [xs >= pweights]
    weights, cost = markowitz_optimizer_3(xs, sigma, lam, mu, new_cons)
    return dict(zip(settings_instruments['id'].values, weights)) if weights.any() else None


def get_setting_weights(settings):
    """
    Returns a dict of weights for each asset from the provided settings object.
    :param settings: The settings to use
    :return: dict from symbol to weight in that setting's portfoloio.
    """
    return {item.asset.id: item.weight for item in settings.portfolio.items.all()}


def get_position_weights(goal):
    """
    Returns a dict of weights for each asset held by a goal against the goal's total holdings.
    :param goal:
    :return: dict from symbol to current weight in that goal.
    """
    res = []
    total = 0.0
    for position in Position.objects.filter(goal=goal).all():
        res.append((position.ticker.id, position.value))
        total += position.value
    return {tid: val/total for tid, val in res}


def get_held_weights(goal):
    """
    Returns a dict of weights for each asset held by a goal against the goal's available balance.
    We use the available balance, not the total held so we can automatically apply any unused cash if possible.
    :param goal:
    :return: dict from symbol to current weight in that goal.
    """
    avail = goal.available_balance
    return {pos.ticker.id: pos.value/avail for pos in Position.objects.filter(goal=goal).all()}


def metrics_changed(goal):
    """
    Return true if the metrics contributing to the goal have changed between the active_settings and the
    approved_settings in any aspect that contributes to new optimal distribution.
    :param goal:
    :return: Boolean (True if changed)
    """
    return goal.active_settings.constraint_inputs() != goal.approved_settings.constraint_inputs()


def build_positions(goal, weights, instruments):
    """
    Returns a set of positions corresponding to the given weights.
    :param goal:
    :param weights:
        An iterable of proportions of each instrument in the portfolio. Position matches instruments.
        The weights should be aligned to orderable quantities.
    :param instruments: Pandas DataFrame of instruments
    :return: A dict from asset id to qty.
    """
    # Establish the positions required for the new weights.
    res = {}
    idloc = instruments.columns.get_loc('id')
    ploc = instruments.columns.get_loc('price')
    avail = goal.available_balance
    for ix, weight in enumerate(weights):
        if weight > MIN_PORTFOLIO_PCT:
            res[instruments.iloc[ix, idloc]] = avail * weight / instruments.iloc[ix, ploc]
    # TODO: Make sure we have landed very near to orderable quantities.
    # TODO: Make sure we are not out of drift now we have made the weights orderable.

    return res


def create_request(goal, positions, reason):
    """
    Create a MarketOrderRequest for the position changes that will take the goal's existing positions to the new
    positions specified.
    :param goal:
    :param positions: A dict from asset id to position
    :param reason: The reason for a change to these positions.
    :return: A MarketOrderRequest and the list of associated ExecutionRequests
    """

    order = MarketOrderRequest(account=goal.account)
    requests = []
    positions = copy.copy(positions)

    # Change any existing positions
    for position in Position.objects.filter(goal=goal).all():
        new_pos = positions.pop(position.ticker.id, 0)
        requests.append(ExecutionRequest(reason=reason,
                                         goal=goal,
                                         asset=position.ticker,
                                         volume=new_pos - position.share,
                                         order=order))

    # Any remaining new positions.
    for tid, pos in positions.items():
        requests.append(ExecutionRequest(reason=reason,
                                         goal=goal,
                                         asset=Ticker.objects.get(id=tid),
                                         volume=pos,
                                         order=order))

    return order, requests


def get_mix_drift(weights, constraints):
    # Get the risk score given the portfolio mix constraints.


def process_risk(weights, min_weights):
    """
    Checks if the weights are within our acceptable risk drift, and if not, perturbates to make it so.
    :param weights:
    :param min_weights:
    :return: (changed,
    """
    pass


def perturbate_risk(min_weights, removals):
    """
    Weighted vol is not the right metric here to rate removability. We want to look at what happens to portfolio risk
    (currently historic variance) when the instrument is removed, rather than looking at the instrument in isolation.
    - While we have drift due to risk > 25% of our threshold,
    - For each performance group, starting from the top, remove assets from the minimal set:
      - If the current risk is higher:
        - Build a group of assets that have increased in volatility*current_weight against the active-portfolio.
            - Prefer an asset that has already been removed
            - Choose the highest volatility*weight delta.
            - Remove enough units from minimal set to bring it's volatility*weight down to the active-portfolio level.
      - If the current risk is lower:
        - Build a group of assets that have decreased in volatility/current_weight against the active-portfolio.
            - Prefer an asset that has already been removed
            - Choose the biggest volatility_weight delta.
            - Remove enough units from minimal set to increase it's volatility/current_weight up to the active-portfolio level.
      - Reoptimise and calculate drift due to risk using the new optimised weights.
    :return: An optimised set of weights that also have acceptable risk_drift
    """
    pass


def perturbate_withdrawal(perf_groups):
    """
    - For each performance group, starting from the top, remove assets until we have a <1 min weight sum scenario.
        - Calculate the drift due to portfolio mix metrics using current minimums
        - while we have overweight drift due to portfolio mix metrics:
            - For each performance group, starting from    the top,
                - Build a group of assets from the overweight features in the current performance group.
                    - Choose the most overweight
                    - Remove enough units to bring its weight to the port weight, available from the active-settings.
            - Then biggest looser / weakest winner first, preferring assets we have already removed..
    :return: A set of weights tht sum to < 1
    """
    pass


def perturbate_mix(perf_groups, min_weights):
    """
    - while we are not satisfiable:
        - Calculate the drift due to portfolio mix metrics using current minimums scaled to sum to 1
        - For each performance group, starting from the top, only doing one instrument at a time..
            - Build a group of assets from the overweight features (or anti-features) in the current performance group.
                - Choose the most overweight
                - Remove enough units to bring its weight to the port weight, available from the active-settings.
                - Try and optimise again

    :return: An optimised set of weights. Always returns weights.
    """

def get_perf_groups(goal):
    """
    - collect all assets into performance groups below:
    - Assets with a short-term loss (< 1 year)
    - Assets with a long-term loss (> 1 year)
    - Assets with a long-term gain (> 1 year)
    - Assets with a short-term gain (< 1 year) (the remaining)


    :return: (STL Perf, LTL Perf, LTG Perf, STG Perf)
        Where a Perf is dict asset_id -> [(perf, volume)]. The list is ordered from biggest loser to biggest winner.
            Where perf is a loss (-) or gain (+) of the double volume amount.
            The reason we have many volumes per ticker is because we can buy or sell lots at different times,
            and hold times are per lot.
    """

    # Assuming the tax rules are FIFO, for each asset, search backwards through the executions until the sum of the buys
    # is greater than or equal to the current position.
    # As I am working back, add each lot to the appropriate result list

    positions = Position.objects.filter()
    executions = Execution.objects.filter()
    pass


def perturbate(goal, idata):
    """
    Jiggle the goal's holdings to fit within the current metrics
    :param goal: The goal who's current holding we want to perturbate to fit the current metrics on the active_settings.
    :returns: (weights, reason)
            - weights: The new weights to use for the goal's holdings that fit within the current constraints (drift_score < 0.25).
            - reason: The reason for the perturbation. (Deposit, Withdrawal or Drift)
    """

    # Optimise the portfolio adding appropriate constraints so there can be no removals from assets.
    # This will use any available cash to rebalance if possible.
    held_weights = get_held_weights(goal)
    opt_inputs = calc_opt_inputs(goal.active_settings, idata)
    weights = optimise_up(opt_inputs, held_weights)

    if weights is None:
        # We have a withdrawal or mix drift, perturbate.
        perf_groups = get_perf_groups(goal)
        if sum(held_weights.values() > 1.0001):
            # We have a withdrawal scenario
            reason = ExecutionRequest.REASON_WITHDRAWAL
            min_weights = perturbate_withdrawal(perf_groups)
            # Then reoptimise using the current minimum weights
            weights = optimise_up(min_weights)
            if weights is None:
                min_weights, weights = perturbate_mix(perf_groups, min_weights)
        else:
            reason = ExecutionRequest.REASON_DRIFT
            min_weights, weights = perturbate_mix(perf_groups, held_weights)

        # By here we should have a satisfiable portfolio, so check and fix any risk_drift
        weights = process_risk(weights, min_weights)

    else:
        # We got a satisfiable optimisation (mix metrics satisfied), now check and fix any risk drift.
        new_weights = process_risk(weights, held_weights)
        if new_weights == weights:
            reason = ExecutionRequest.REASON_DEPOSIT
        else:
            reason = ExecutionRequest.REASON_DRIFT
            weights = new_weights

    return weights, reason


def rebalance(goal, idata):
    """
    Rebalance Strategy:
    :param goal: The goal to rebalance
    :param idata: The current instrument data
    :return:
    """

    # If our important metrics were changed, all attempts to perturbate the old holdings is avoided, and we simply
    # apply the new desired weights.
    optimal_weights = get_setting_weights(goal.approved_settings)
    if metrics_changed(goal):
        weights = optimal_weights
        reason = ExecutionRequest.REASON_METRIC_CHANGE
    else:
        # The important metrics weren't changed, so try and perturbate.
        weights, reason = perturbate(goal, idata)

        # TODO: check the difference in execution cost (including tax impact somehow) between optimal and weights,
        # TODO: use whichever better.
    new_positions = build_positions(goal, weights, settings_instruments)
    return create_request(goal, new_positions, reason)
