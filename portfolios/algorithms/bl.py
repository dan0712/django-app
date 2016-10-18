import numpy as np
from numpy.linalg import inv
from statsmodels.stats.correlation_tools import cov_nearest
import logging

logger = logging.getLogger("portfolios.algorithms.bl")


def bl_model(sigma, w_tilde, p, v, n, c=1.0, lambda_bar=1.2):
    """
    This is an implementation of the Black-Litterman model based
    on Meucci's article:

    http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1117574

    Argument Definitions:
      Required:
        :param sigma: nxn numpy array covariance matrix of the asset
                      return time series
        :param w_tilde: nx1 numpy array market cap portfolio weights
        :param p: mxn numpy array corresponding to investor views on
                  future asset movements
        :param v: mx1 numpy array of expected returns of portfolios
                  corresponding to views
        :param n: length of time series of returns used to compute
                  covariance matrix
        :param c: constant representing overall confidence in the views
                  return estimator
        :param lambda_bar: risk-aversion level which Black and
                           Litterman set to 1.2

    Argument Constraints:
        Required:
        sigma -- positive definite symmetric matrix
        w_tilde -- vector with positive entries that sum to one
        p -- matrix of positive or negative floats
        v -- matrix of positive or negative floats

        Optional:
        c -- any positive float, default to 1 (as in example on page 5)
        lambda_bar -- positive float, default to 1.2 as mentioned
                      after equation (5)
    """
    logger.debug("Running BL with "
                 "sigma:\n{}\nw_tilde:\n{}\np:\n{}\nv:\n{}\nn:{}"
                 .format(sigma, w_tilde, p, v, n))

    pi = 2.0 * lambda_bar * np.dot(sigma, w_tilde)  # equation (5)
    tau = 1.0 / float(n)  # equation (8)

    omega = np.dot(np.dot(p, sigma), p.T) / c  # equation (12)

    # Main model, equations (20) and (21)
    m1 = np.dot(tau * np.dot(sigma, p.T),
                inv(tau * np.dot(p, np.dot(sigma, p.T)) + omega))
    m2 = v - np.dot(p, pi)
    m3 = np.dot(p, sigma)

    mu_bl = pi + np.dot(m1, m2)
    sig_bl = (1.0 + tau) * sigma - tau * np.dot(m1, m3)

    # Make the matrix symmetric
    sym_bl = (sig_bl + sig_bl.T) / 2

    # The cov matrix may have not been strictly pos semi definite
    # due to rounding etc. Make sure it is.
    psd_bl = cov_nearest(sym_bl)

    return mu_bl, psd_bl