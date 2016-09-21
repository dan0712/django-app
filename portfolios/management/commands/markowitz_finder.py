import logging

import numpy as np
from cvxpy import mul_elemwise
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from portfolios.algorithms.markowitz import markowitz_optimizer_3
from portfolios.calculation import MIN_PORTFOLIO_PCT, get_core_constraints, get_instruments, \
    INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL
from portfolios.markowitz_scale import get_risk_curve
from portfolios.providers.data.django import DataProviderDjango

logger = logging.getLogger("markowitz_finder")

class Command(BaseCommand):
    help = 'Calculate all the optimal portfolios for ' \
           'all the goals in the system.'

    def handle(self, *args, **options):
        # find extremes
        data_provider = DataProviderDjango()
        # Get the funds from the instruments table
        covars, funds, masks = get_instruments(data_provider)
        sigma = covars.values

        mu = funds[INSTRUMENT_TABLE_EXPECTED_RETURN_LABEL].values

        # Get the instrument with the best BL ER.
        perfix = np.argmax(mu)
        logger.info("Found largest ER instrument: {} at index: {}".format(funds.index[perfix], perfix))

        xs, constraints = get_core_constraints(funds.shape[0])

        constraints += [xs >= 0]

        # Find the lambda that gives only the best BL ER.
        lowerb = 0.0
        upperb = 100000000.0
        mval = 10
        while upperb - lowerb > .001:  # We want lambda to 3 decimal places
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

        vals = get_risk_curve(min_lambda, max_lambda)

        data_provider.set_markowitz_scale(dt=now().today(),
                                          mn=min_lambda,
                                          mx=max_lambda,
                                          a=vals[0],
                                          b=vals[1],
                                          c=vals[2])
