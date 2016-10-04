'''
Deciding when to rebalance:
 - A user can decide to "Rebalance Now". If the "Rebalance now" button is pressed. Make sure we display to the user
   what the estimated cost of the rebalance is and how it compares to the ATCS.
'''
import logging

import copy
import numpy as np

from portfolios.algorithms.markowitz import markowitz_optimizer_3
from portfolios.calculation import MIN_PORTFOLIO_PCT, \
    calc_opt_inputs, create_portfolio_weights, INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL
from portfolios.providers.execution.abstract \
    import Reason, ExecutionProviderAbstract

from main.models import GoalMetric, Ticker, AssetFeature, AssetFeatureValue, PositionLot
from collections import defaultdict
from django.db.models import Sum, F, Case, When, Value, FloatField
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import operator

logger = logging.getLogger('rebalance')

tax_bracket_less1Y = 0.3
tax_bracket_more1Y = 0.2

def optimise_up(opt_inputs, min_weights):
    """
    Reoptimise the portfolio adding appropriate constraints so there can be no removals from assets.
    :param opt_inputs: The basic optimisation inputs for this goal.
    :param min_weights: A dict from asset_id to new minimum weight.
    :return: weights - The new dict of weights, or None if impossible.
    """
    xs, lam, constraints, settings_instruments, settings_symbol_ixs, instruments, lcovars = opt_inputs

    mu = settings_instruments[INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL].values
    pweights = create_portfolio_weights(settings_instruments['id'].values, min_weights=min_weights, abs_min=0)
    new_cons = constraints + [xs >= pweights]
    weights, cost = markowitz_optimizer_3(xs, lcovars.values, lam, mu, new_cons)
    return dict(zip(settings_instruments['id'].values, weights)) if weights.any() else None


def get_setting_weights(settings):
    """
    Returns a dict of weights for each asset from the provided settings object.
    :param settings: The settings to use
    :return: dict from symbol to weight in that setting's portfoloio.
    """
    return {item.asset.id: item.weight for item in settings.get_portfolio_items_all()}


def get_position_weights(goal):
    """
    Returns a dict of weights for each asset held by a goal against the goal's total holdings.
    :param goal:
    :return: dict from symbol to current weight in that goal.
    """
    res = []
    total = 0.0
    for position in goal.get_positions_all():
        res.append((position['ticker_id'], position['quantity'] * position['price']))
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
    return {pos['ticker_id']: (pos['quantity'] * pos['price'])/avail for pos in goal.get_positions_all()}


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
    for ix, weight in weights.items():
        if weight > MIN_PORTFOLIO_PCT:
            res[ix] = int(avail * weight / instruments.ix[ix, ploc])

    # orderable quantitites will probably always be in single units of shares (ETFs).
    # TODO: Make sure we have landed very near to orderable quantities.
    # TODO: Make sure we are not out of drift now we have made the weights orderable.

    return res


def create_request(goal, new_positions, reason, execution_provider, data_provider):
    """
    Create a MarketOrderRequest for the position changes that will take the goal's existing positions to the new
    positions specified.
    :param goal:
    :param positions: A dict from asset id to position
    :param reason: The reason for a change to these positions.
    :return: A MarketOrderRequest and the list of associated ExecutionRequests
    """

    order = execution_provider.create_market_order(account=goal.account)
    requests = []
    new_positions = copy.copy(new_positions)

    # Change any existing positions
    positions = goal.get_positions_all()
    for position in positions:

        new_pos = new_positions.pop(position['ticker_id'], 0)
        if new_pos - position['quantity'] == 0:
            continue
        ticker = data_provider.get_ticker(id=position['ticker_id'])
        request = execution_provider.create_execution_request(reason=reason,
                                                              goal=goal,
                                                              asset=ticker,
                                                              volume=new_pos - position['quantity'],
                                                              order=order,
                                                              limit_price=None)
        requests.append(request)

    # Any remaining new positions.
    for tid, pos in new_positions.items():
        if pos == 0:
            continue
        ticker = data_provider.get_ticker(id=tid)
        request = execution_provider.create_execution_request(reason=reason,
                                                              goal=goal,
                                                              asset=ticker,
                                                              volume=pos,
                                                              order=order,
                                                              limit_price=None)
        requests.append(request)

    return order, requests


def get_mix_drift(weights, constraints):
    '''
    :param weights:
    :param constraints:
    :return:
    '''
    # Get the risk score given the portfolio mix constraints.


def process_risk(weights, min_weights):
    """
    Checks if the weights are within our acceptable risk drift, and if not, perturbates to make it so.
    :param weights:
    :param min_weights:
    :return: (changed,
    """
    return weights


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
    use specific lots technique - so perf. groups will not help, but we will need to calculate lots for current holding, calculate specific lots for holding
     and then start selling largest tax gain to largest tax loss (largest losers to largest winners)
     To use specific lots technique, we need to know tax burden 1Y> and 1Y<, e.g. 28% vs 15%

     specific lots vs. getting close to portfolio mix (in active_settings.portfolio.portfolio_items vs current holdings?)
-------------------------------------------------------------------------------
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


def perturbate_mix(goal, min_weights):
    """
                        order assets into groups of metrics constraints - compare with metrics constraints in settings
                        go into group with biggest difference - start selling assets from the group (from lowest tax loss further)
                        until sum of current assets in group == metric constraint for that group
                        try to find solution
                        repeat until solution found
    """
    metrics = GoalMetric.objects.\
        filter(group__settings__goal_active=goal).\
        filter(type=GoalMetric.METRIC_TYPE_PORTFOLIO_MIX).\
        filter(Q(comparison=GoalMetric.METRIC_COMPARISON_EXACTLY) |
               Q(comparison=GoalMetric.METRIC_COMPARISON_MAXIMUM))
        #only exact or maximums - we are interested in sells only

    year_ago = timezone.now() - timedelta(days=365)
    position_lots = PositionLot.objects.filter(quantity__gt=0) \
                        .filter(execution_distribution__transaction__from_goal=goal) \
                        .annotate(price=F('execution_distribution__execution__price'),
                                  executed=F('execution_distribution__execution__executed'),
                                  current_price=F('execution_distribution__execution__asset__unit_price'),
                                  ticker_id=F('execution_distribution__execution__asset_id')) \
                        .annotate(tax_bracket=Case(
                          When(executed__gt=year_ago, then=Value(tax_bracket_less1Y)),
                          When(executed__lte=year_ago, then=Value(tax_bracket_more1Y)),
                          output_field=FloatField())) \
                        .annotate(unit_tax_cost=(F('current_price') - F('price')) * F('tax_bracket')) \
                        .values('id', 'price', 'quantity', 'executed', 'unit_tax_cost','ticker_id','current_price') \
                        .order_by('-unit_tax_cost')

    metrics_weights = defaultdict(defaultdict)
    for metric in metrics:
        asset_ids = AssetFeatureValue.objects.all().filter(id=metric.feature_id)\
            .annotate(ticker_id=F('assets__id'))\
            .values_list('ticker_id', flat=True).distinct()

        measured_val = _get_measured_val(position_lots, asset_ids, goal)
        drift = _get_drift(measured_val, metric)

        metrics_weights[metric.id]['asset_ids'] = asset_ids
        metrics_weights[metric.id]['drift'] = drift

    to_be_sorted = dict()
    for metric_id, value in metrics_weights.items():
        if value['drift'] > 0:
            to_be_sorted[metric_id] = value['drift']
    sorted_positive_drifts = sorted(to_be_sorted.items(), key=lambda x: -x[1]) #desc

    desired_lots = position_lots[:]
    for metric_id, drift in sorted_positive_drifts:
        # we are in group with biggest difference now
        metric = [m for m in metrics if m.id == metric_id][0]
        _sell_quantity(desired_lots, metrics_weights[metric_id]['asset_ids'], goal, metric)

    weights = get_weights(desired_lots, goal.available_balance)
    return weights


def get_weights(lots, available_balance):
    """
    Returns a dict of weights for each asset held by a goal against the goal's available balance.
    We use the available balance, not the total held so we can automatically apply any unused cash if possible.
    :param goal:
    :return: dict from symbol to current weight in that goal.
    """
    weights = defaultdict(float)
    for lot in lots:
        weights[lot['ticker_id']] += (lot['quantity'] * lot['price'])/available_balance
    return weights


def _get_measured_val(position_lots, asset_ids, goal):
    """
    :param position_lots: list of tuples, where each tuple contains info for position lot ('id', 'price', 'quantity', 'executed', 'unit_tax_cost')
    :param asset_ids: list of asset ids which belong to given metric
    :param goal: Goal
    :return:
    The function duplicates GoalMetric.measured_val - but does all calculation on in-memory data structures
    """
    amount_shares = float(np.sum(
        [pos['current_price'] * pos['quantity'] if pos['ticker_id'] in asset_ids else 0 for pos in position_lots]
    ))
    return amount_shares / goal.available_balance


def _get_drift(measured_val, goal_metric):
    """
    :param measured_val: measured_val from GoalMetric model
    :param goal_metric: GoalMetric
    :return:
    The function duplicates GoalMetric.get_drift - but does all calculation on in-memory measured_val
    """
    if goal_metric.rebalance_type == GoalMetric.REBALANCE_TYPE_ABSOLUTE:
        return (measured_val - goal_metric.configured_val) / goal_metric.rebalance_thr
    else:
        return ((measured_val - goal_metric.configured_val) / goal_metric.configured_val) / goal_metric.rebalance_thr


def _sell_quantity(position_lots, asset_ids, goal, metric):
    """
    how much to sell to get to drift 0
    :param position_lots: list of tuples, where each tuple contains info for position lot ('id', 'price', 'quantity', 'executed', 'unit_tax_cost')
    :param asset_ids: list of asset ids which belong to given metric
    :param goal: Goal
    :return:
    try selling whole lots until we are in tolerance or we have surpassed if.
    if we surpassed tolerance, try to get back by increasing sold lot by 0.01
    """

    measured_val = _get_measured_val(position_lots, asset_ids, goal)
    drift = _get_drift(measured_val, metric)
    if abs(drift) < 1:
        return

    for lot in position_lots:
        if not lot['ticker_id'] in asset_ids:
            continue

        lot['quantity'] = 0
        measured_val = _get_measured_val(position_lots, asset_ids, goal)
        drift = _get_drift(measured_val, metric)

        while drift < -1:
            lot['quantity'] += 0.01
            measured_val = _get_measured_val(position_lots, asset_ids, goal)
            drift = _get_drift(measured_val, metric)

        if abs(drift) < 1:
            break


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
    # As I am working back, add each lot to the
    #  appropriate result list

    #positions = Position.objects.filter()
    #executions = Execution.objects.filter()
    pass


def get_largest_min_weight_per_asset(held_weights,tax_weights):
    min_weights = dict()
    for w in held_weights.items():
        if w[0] in tax_weights:
            min_weights[w[0]] = max(float(tax_weights[w[0]]), float(w[1]))
        else:
            min_weights[w[0]] = float(w[1])
    return min_weights


def perturbate(goal, idata, data_provider, execution_provider):
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
    tax_min_weights = execution_provider.get_asset_weights_held_less_than1y(goal, data_provider.get_current_date())
    min_weights = get_largest_min_weight_per_asset(held_weights=held_weights, tax_weights=tax_min_weights)
    opt_inputs = calc_opt_inputs(goal.active_settings, idata, data_provider, execution_provider)
    weights = optimise_up(opt_inputs, min_weights)

    if weights is None:
        # relax constraints and allow to sell tax winners
        tax_min_weights = execution_provider.get_asset_weights_without_tax_winners(goal=goal)
        min_weights = get_largest_min_weight_per_asset(held_weights=held_weights, tax_weights=tax_min_weights)
        weights = optimise_up(opt_inputs, min_weights)

    if weights is None:
        # We have a withdrawal or mix drift, perturbate.
        perf_groups = get_perf_groups(goal)
        if sum(held_weights.values()) > 1.0001:
            # We have a withdrawal scenario

            reason = execution_provider.get_execution_request(Reason.WITHDRAWAL.value)
            min_weights = perturbate_withdrawal(perf_groups)
            # Then reoptimise using the current minimum weights
            weights = optimise_up(min_weights)
            if weights is None:
                min_weights, weights = perturbate_mix(goal)
        else:
            reason = execution_provider.get_execution_request(Reason.DRIFT.value)
            weights = perturbate_mix(goal)

        # By here we should have a satisfiable portfolio, so check and fix any risk_drift
        weights = process_risk(weights, min_weights)

    else:
        # We got a satisfiable optimisation (mix metrics satisfied), now check and fix any risk drift.
        new_weights = process_risk(weights, held_weights)

        if new_weights == weights:
            reason = execution_provider.get_execution_request(Reason.DEPOSIT.value)
        else:
            reason = execution_provider.get_execution_request(Reason.DRIFT.value)
            weights = new_weights

    return weights, reason


def rebalance(goal, idata, data_provider, execution_provider):
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
        reason = execution_provider.get_execution_request(ExecutionProviderAbstract.Reason.METRIC_CHANGE.value)
    else:
        # The important metrics weren't changed, so try and perturbate.
        weights, reason = perturbate(goal, idata, data_provider=data_provider, execution_provider=execution_provider)

        # TODO: check the difference in execution cost (including tax impact somehow) between optimal and weights,
        # TODO: use whichever better.

        # The algo should rebalance whenever the Expected Return on the rebalance is greater than the expected excecution cost

        #The expected return on the rebalancing should be: The cost of not being optimal (the utility cost function of
        #drift of the portfolio)
        #Normally it should be consistent with the optimizing function
        #Minimize(quad_form(x, sigma) - lam * mu * x)
        #So the proposed function will be :
        # markowitz_cost(diff of weights, other params)
        #SHould I take into account the building of the tax algo?, if so, how are the trades being stored? and where?

        #trades are stored in execution_provider.executions, which is a list, as ExecutionMock() or Execution() classes.

        #A goal is a portfolio? If the rebalance is being made by goal it could be inneficient from a cost perspective

    new_positions = build_positions(goal, weights, idata[2])
    #idata[2] is a matrix containing latest instrument price
    order = create_request(goal, new_positions, reason,
                           execution_provider=execution_provider,
                           data_provider=data_provider)
    transaction_cost = np.sum([abs(request.volume) for request in order[1]]) * 0.005
    # So, the rebalance could not be in place if the excecution algo might not determine how much it will cost to rebalance.

    return order
