import datetime
import logging
import numpy as np

from cvxpy import mul_elemwise
from django.core.management.base import BaseCommand
from scipy.optimize.minpack import curve_fit

from main.models import MarkowitzScale
from portfolios.BL_model.bl_model import bl_model, markowitz_optimizer_3
from portfolios.management.commands.portfolio_calculation import get_instruments, get_market_caps, \
    get_core_constraints, MIN_PORTFOLIO_PCT

logger = logging.getLogger("markowitz_finder")
logger.setLevel(logging.DEBUG)


def get_extremes():
    covars, samples, instruments, masks = get_instruments()

    # Get the instrument with the best implied equilibrium return.
    market_caps = get_market_caps(instruments)
    instruments['iew'] = covars.dot(market_caps)
    sted = instruments.sort('iew', ascending=False)
    perfix = instruments.index.get_loc(sted.index[0])
    logger.info("Found best performer: {} at index: {}".format(instruments.index[perfix], perfix))

    # At the moment we're ignoring views..
    # TODO: Add view logic. I.e. Have markowitz limits per portfolio set.
    # views, vers = get_views(goal, goal_instruments)

    xs, constraints = get_core_constraints(instruments.shape[0])

    # Pass the data to the BL algorithm to get the the mu and sigma for the optimiser
    mu, sigma = bl_model(covars.values,
                         market_caps.values,
                         np.zeros((0, instruments.shape[0])),
                         [],
                         samples)

    # Find the lambda that gives only the most performant.
    lowerb = 0.0
    upperb = 100000000.0
    mval = 10
    while upperb-lowerb > .001:  # We want lambda to 3 decimal places
        weights, cost = markowitz_optimizer_3(xs, sigma, mval, mu, constraints)
        changed = False
        for ix, weight in enumerate(weights):
            # print("ix={}, weight={}".format(ix, weight))
            if ix != perfix and weight > MIN_PORTFOLIO_PCT:
                lowerb = mval
                mval = min(mval * 2, mval + ((upperb - mval) / 2))
                changed = True
                break
        if not changed:
            upperb = mval
            mval -= ((mval - lowerb) / 2)

    max_lambda = round(mval, 3)
    logger.info("Found MAX_LAMBDA: {}".format(max_lambda))

    # Find the least variance portfolio.
    constraints.append(mul_elemwise(mu, xs) >= 0)
    weights, cost = markowitz_optimizer_3(xs, sigma, 0.0, mu, constraints)
    # Remove any below minimum percent and round to find the target portfolio
    weights[weights < MIN_PORTFOLIO_PCT] = 0
    target = np.round(weights, 2)

    # Find the lambda that gives the same portfolio as the target.
    lowerb = 0.0
    upperb = max_lambda
    mval = max_lambda / 2
    while upperb-lowerb > .001:  # We want lambda to 3 decimal places
        weights, cost = markowitz_optimizer_3(xs, sigma, mval, mu, constraints)
        weights[weights < MIN_PORTFOLIO_PCT] = 0
        comp = np.round(weights, 2)
        if np.allclose(target, comp):
            lowerb = mval
            mval += ((upperb - mval) / 2)
        else:
            upperb = mval
            mval -= ((mval - lowerb) / 2)

    min_lambda = round(mval, 3)
    logger.info("Found MIN_LAMBDA: {}".format(min_lambda))

    x = [-50, 0, 50]
    y = [min_lambda, 1.2, max_lambda]

    def func(x, a, b, c):
        return a * np.power(b, x) + c

    vals, _ = curve_fit(func, x, y)
    logger.info("Found function fit using params: {}".format(vals))

    MarkowitzScale.objects.create(date=datetime.datetime.today(),
                                  min=min_lambda,
                                  max=max_lambda,
                                  a=vals[0],
                                  b=vals[1],
                                  c=vals[2])


class Command(BaseCommand):
    help = 'Calculate all the optimal portfolios for all the goals in the system.'

    def handle(self, *args, **options):
        get_extremes()
