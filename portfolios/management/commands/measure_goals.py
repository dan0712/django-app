"""
    - Calculate the current weights of the symbols in the portfolio given their current prices and volumes held.
    - Using the current covariance matrix, current expected returns and calculated weights, do a Markowitz optimisation
      but using the Markowitz Lambda as the free variable.
    - Determine at what percentage between the current MIN_LAMBDA and MAX_LAMBDA the calculated Lambda sits. This is the
      current calculated Normalised Risk Score for the portfolio.
    - Risk Drift is the percentage difference between The goal's saved normalised risk score and the current calculated
      normalised risk score.
"""
import logging
import math
from collections import defaultdict

import numpy as np
from django.core.management.base import BaseCommand
from django.db import transaction
from scipy.optimize import minimize_scalar

from main.models import Goal, GoalMetric, Position
from portfolios.bl_model import markowitz_cost
from portfolios.calculation import Unsatisfiable, \
    lambda_to_risk_score, optimize_settings, run_bl
from portfolios.management.commands.portfolio_calculation import get_instruments
from portfolios.providers.data.django import DataProviderDjango

logger = logging.getLogger("measure_goals")
# logger.setLevel(logging.DEBUG)


def get_weights(goal):
    """
    Returns a list of current percentage weights for each ticker in a goal.
    :param goal:
    :return: dict from symbol to current weight in that goal.
    """
    res = []
    total = 0.0
    for position in Position.objects.filter(goal=goal).all():
        res.append((position.ticker.symbol, position.value, position.ticker.features.values_list('id', flat=True)))
        total += position.value
    return [(sym, val/total, fids) for sym, val, fids in res]


def get_risk_score(goal, weights, idata):
    """
    Returns the risk score for the provided weights.
    :param goal:
    :param weights:
    :param idata:
    :return:
    """
    if len(weights) == 0:
        logger.info("No holdings for goal: {} so current risk score is 0.".format(goal))
        return 0.0

    # Get the cost of a clean optimisation using the current constraints.
    current_cost = optimize_settings(goal.active_settings, idata)[1]

    # Set up the required data
    covars, samples, instruments, masks = idata
    instruments['_weight_'] = 0.0
    # Build the indexes from the passed in weights
    goal_symbol_ixs = []
    for sym, weight, _ in weights:
        goal_symbol_ixs.append(instruments.index.get_loc(sym))
        instruments.loc[sym, '_weight_'] = weight

    goal_instruments = instruments.iloc[goal_symbol_ixs]
    mu, sigma = run_bl(instruments, covars, goal_instruments, samples, goal.portfolio_set)
    ws = np.expand_dims(goal_instruments['_weight_'].values, 0)

    # Get the lambda that produces the same cost as the optimum portfolio using the configured risk score.
    # TODO: I can probably do this algebraically, and not have to run an iterative minimizer, but this is easy for now.
    def f(lam):
        cost = markowitz_cost(ws, sigma, lam, mu)
        return abs(current_cost - cost)
    res = minimize_scalar(f)
    if math.isnan(res.x):
        raise Exception("Couldn't find appropriate lambda")

    logger.debug("Calculated lambda: {} for goal: {}".format(res.x, goal))
    return lambda_to_risk_score(lam=res.x,
                                data_provider=DataProviderDjango())


def measure(goal, idata):
    """
    Measure all the metrics on a goals's active settings, and set the maximum drift for the goal.
    :param goal:
    :param idata:
    :return:
    """
    if goal.active_settings is None:
        logger.debug("Not measuring metrics for goal: {} as it has no active settings.".format(goal))
        return

    weights = get_weights(goal)
    # Generate a feature -> weight map
    feature_weights = defaultdict(float)
    for _, weight, fids in weights:
        for fid in fids:
            feature_weights[fid] += weight
    try:
        risk_score = get_risk_score(goal, weights, idata)
    except Unsatisfiable:
        logger.exception("Cannot get the current risk score.")
        risk_score = None

    with transaction.atomic:
        drift_score = 0.0
        for metric in goal.active_settings.metric_group.metrics.all():
            if metric.type == GoalMetric.METRIC_TYPE_RISK_SCORE:
                logger.debug("Setting measured risk score: {} for metric: {}".format(risk_score, metric))
                metric.measured_val = risk_score
            elif metric.type == GoalMetric.METRIC_TYPE_PORTFOLIO_MIX:
                val = feature_weights[metric.feature.id]
                logger.debug("Setting measured proportion: {} for metric: {}".format(val, metric))
                metric.measured_val = val
            else:
                raise Exception("Unknown type on metric: {}".format(metric))
            drift_score = max(drift_score, abs(metric.drift_score))
            metric.save()
        goal.drift_score = drift_score
        goal.save()


class Command(BaseCommand):
    help = 'Measure and record all the metrics for all the goals in the system.'

    def handle(self, *args, **options):
        idata = get_instruments()
        for goal in Goal.objects.all():
            measure(goal, idata)
