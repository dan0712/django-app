import logging

import numpy as np
from cvxpy import mul_elemwise
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from scipy.optimize.minpack import curve_fit

from portfolios.bl_model import markowitz_optimizer_3
from portfolios.calculation import FUND_MASK_NAME, \
    MIN_PORTFOLIO_PCT, get_core_constraints, run_bl
from portfolios.providers.data.django import DataProviderDjango

logger = logging.getLogger("markowitz_finder")


class Command(BaseCommand):
    help = 'Calculate all the optimal portfolios for ' \
           'all the goals in the system.'

    def handle(self, *args, **options):
        # find extremes
        data_provider = DataProviderDjango()
        # Get the funds from the instruments table
        covars, samples, instruments, masks = data_provider.get_instruments()
        funds = instruments[masks[FUND_MASK_NAME]]

        # Generate the BL ERs and Sigma
        # TODO: Add views. I.e. Have markowitz limits per portfolio set.
        mu, sigma = run_bl(instruments, covars, funds, samples, None)

        # Get the instrument with the best BL ER.
        perfix = np.argmax(mu)
        logger.info("Found largest BL ER instrument: {} at index: {}".format(
            funds.index[perfix], perfix))

        xs, constraints = get_core_constraints(funds.shape[0])

        # Find the lambda that gives only the best BL ER.
        lowerb = 0.0
        upperb = 100000000.0
        mval = 10
        while upperb - lowerb > .001:  # We want lambda to 3 decimal places
            weights, cost = markowitz_optimizer_3(xs, sigma, mval, mu,
                                                  constraints)
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
        while upperb - lowerb > .001:  # We want lambda to 3 decimal places
            weights, cost = markowitz_optimizer_3(xs, sigma, mval, mu,
                                                  constraints)
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

        data_provider.set_markowitz_scale(date=now().today(),
                                          min=min_lambda,
                                          max=max_lambda,
                                          a=vals[0],
                                          b=vals[1],
                                          c=vals[2])
