import logging
from datetime import timedelta, datetime

import math
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.optimize._minimize import minimize_scalar

MAX_RISK_SCORE = 1
MIN_RISK_SCORE = 0

logger = logging.getLogger(__name__)


def risk_score_to_lambda(risk_score, data_provider):
    scale = data_provider.get_markowitz_scale()
    if scale is None:
        raise Exception("No Markowitz limits available. Cannot convert The risk score into a Markowitz lambda.")
    scale_date = scale.date
    if scale_date < (data_provider.get_current_date() - timedelta(days=7)):
        logger.warn("Most recent Markowitz scale is from {}.".format(scale.date))
    return _to_lambda(risk_score, scale.a, scale.b, scale.c)


def lambda_to_risk_score(lam, data_provider):
    # Turn the markowitz lambda into a risk score
    scale = data_provider.get_markowitz_scale()
    if scale is None:
        raise Exception("No Markowitz limits available. Cannot convert The Markowitz lambda into a risk score.")
    scale_date = pd.Timestamp(scale.date).to_datetime()
    if scale_date < (datetime.now().today() - timedelta(days=7)):
        logger.warn("Most recent Markowitz scale is from {}.".format(scale.date))
    return _to_risk_score(lam, scale.a, scale.b, scale.c)


def _to_lambda(risk_score, a, b, c):
    """
    Converts risk score to lambda using given function parameters
    a = .355
    b = -.711
    c = .0000006
    """
    return a - ((b / c) * (1 - np.exp(-c * risk_score)))


def _to_risk_score(lam, a, b, c):
    """
    Converts lambda to risk score
    """
    def f(risk_score):
        lam2 = _to_lambda(risk_score, a, b, c)
        return abs(lam2 - lam)

    # TODO: There's gotta be a better way to do this. This is just overkill
    res = minimize_scalar(f)
    if math.isnan(res.x):
        raise Exception("Couldn't find appropriate risk score")

    return res.x


def get_risk_curve(min_lambda, max_lambda):
    """

    :param max_lambda: The maximum lambda score for the day
    :param min_lambda: The minimum lambda score for the day
    :return: (a, b, c) - Three parameters for the risk curve function.
    """
    x = [MIN_RISK_SCORE, (MIN_RISK_SCORE+MAX_RISK_SCORE)/2, MAX_RISK_SCORE]
    y = [min_lambda, min((max_lambda + min_lambda) / 2, 1.2), max_lambda]

    vals, _ = curve_fit(_to_lambda, x, y)
    logger.info("Found function fit using params: {}".format(vals))
    return vals
