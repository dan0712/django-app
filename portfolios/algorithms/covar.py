import logging

import numpy as np
from sklearn.covariance import OAS

from portfolios.calculation import logger
from common.constants import WEEKDAYS_PER_YEAR


def lw_covars(returns):
    """
    Calculates a constrained covariance matrix between the returns.
    :return: A pandas dataframe of the covariance between the returns
    """
    co_vars = returns.cov() * WEEKDAYS_PER_YEAR

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Calcing covars as table: {}".format(returns.to_dict('list')))

    # Shrink the covars (Ledoit and Wolff)
    sk = OAS(assume_centered=True)
    sk.fit(returns.values)
    return (1 - sk.shrinkage_) * co_vars + sk.shrinkage_ * np.trace(co_vars) / len(co_vars) * np.identity(len(co_vars))