import logging

import numpy as np
import scipy.optimize
from cvxpy import Minimize, Problem, Variable, quad_form, sum_entries
from numpy import cov, dot, sqrt, transpose
from numpy.linalg import inv
from sklearn.covariance import OAS
from statsmodels.stats.correlation_tools import cov_nearest

from portfolios.exceptions import OptimizationException, OptimizationFailed

logger = logging.getLogger('betasmartz.bl_model')


def calculate_co_vars(assets_len, table):
    columns = list(table)
    sk = OAS(assume_centered=True)
    sk.fit(table.pct_change().dropna().values)

    # calculate covariance matrix
    co_vars = np.zeros([assets_len, assets_len])
    for i in range(assets_len):

        var_table = table.reindex(index=None,
                                  columns=[columns[i], columns[i]])
        monthly_returns_i_i = var_table.pct_change().dropna().values.T
        co_vars_i_i = assets_covariance(monthly_returns_i_i)
        co_vars[i, i] = co_vars_i_i[0, 1]

        for j in range(i + 1, assets_len):
            # covariance
            new_table = table.reindex(index=None,
                                      columns=[columns[i], columns[j]])
            monthly_returns_i_j = new_table.pct_change().dropna().values.T
            co_vars_i_j = assets_covariance(monthly_returns_i_j)
            co_vars[j, i] = co_vars[i, j] = co_vars_i_j[0, 1]
    # annualized
    sk_co_var = ((1 - sk.shrinkage_) * co_vars +
                 sk.shrinkage_ * np.trace(co_vars) /
                 assets_len * np.identity(assets_len))
    return sk_co_var, co_vars


# Compute the expected return of the portfolio.
def compute_mean(W, R):
    return sum(R * W)


# Compute the variance of the portfolio.
def compute_var(W, C):
    return dot(dot(W, C), W)


def var_gradient(W, C):
    return dot(W, C) + dot(W, np.diag(np.diag(C)))


def compute_mean_var(W, R, C):
    """
    Combination of the two functions above - mean and variance of
    returns calculation.
    """
    return compute_mean(W, R), compute_var(W, C)


def fitness(W, R, C, r, assets_type, allocation, constrains, iW, order, bonds):
    w_w = 10000
    w_er = 100
    w_sqrt = 100
    # For given level of return r,
    # find weights which minimizes portfolio variance.
    mean_1, var = compute_mean_var(W, R, C)
    # Penalty for not meeting stated portfolio return effectively serves as
    # optimization constraint
    # Here, r is the 'target' return
    jac = np.zeros(len(W))
    func = 0
    # expected returns function
    func = -w_er * mean_1
    # jac mean
    jac += -w_er * R

    # variance
    func += w_sqrt * sqrt(var)
    var_jac = var_gradient(W, C) / (2 * sqrt(var))
    jac += w_sqrt * var_jac

    # ====================================================
    #               portfolio weights
    # ==================================================
    # 100% weight
    func += w_w * ((sum(W) - 1) ** 2)
    jac += w_w * (2 * (sum(W) - 1) * np.ones(len(W)))

    # Allocation stock
    func += w_w * ((dot(assets_type, W) - allocation) ** 2)
    jac += w_w * (2 * (dot(assets_type, W) - allocation) * assets_type)
    bond_allocation = 1 - allocation

    # Allocation bonds
    func += w_w * ((dot(bonds, W) - bond_allocation) ** 2)
    jac += w_w * (2 * (dot(bonds, W) - bond_allocation) * bonds)

    for ct in constrains:
        v, new_jac = ct(order, W)
        func += w_w * v
        jac += w_w * new_jac

    if (allocation != 0) and (allocation != 1):
        func += 10 * sum((W - iW) ** 2)
        jac += 10 * 2 * (W - iW)

    return np.around(func, decimals=10), np.around(jac, decimals=10)


# Solve for optimal portfolio weights
def solve_weights(R, C, risk_free, allocation, assets_type,
                  constrains, iW, order):
    assets_type = np.array(assets_type)

    n = len(R)
    W = iW
    tol = 0.00001
    bonds = list(map(lambda x: 0 if x == 1 else 1, assets_type))
    bonds = np.array(bonds)
    b_ = [(0, 1) for i in range(n)]  # Bounds for decision variables
    # Constraints - weights must sum to 1
    # sum of weights of stock should be equal to allocation
    # 'target' return is the expected return on the market portfolio
    optimized = scipy.optimize.minimize(
        fitness, W,
        (R, C, sum(R * W), assets_type, allocation, constrains, iW, order,
         bonds),
        jac=True,
        method='SLSQP', bounds=b_, tol=tol, options={"maxiter": 1000})
    if not optimized.success:
        raise OptimizationException(optimized.message)

    return optimized.x


# Covars - covariance matrix of asset returns based on historical data
def assets_covariance(monthly_returns):
    # Compute covariance matrix
    co_vars = cov(monthly_returns)
    # Annualized expected returns and covariances
    # Assumes 12 trading months per year
    return co_vars * 12


def handle_data(n, expected_returns, sk_co_var, co_vars, risk_free,
                allocation, assets_type, views, qs, tau,
                constrains, mw, initial_w, order):
    """
    all prices: table with the monthly closed price for each asset
    risk_free: risk free rate
    asset_type: list (0,0,0,1,1,1), where 1 means that is a stock and 0
                that is a bond
    allocation: number between 0-1, 0-means all in bond, 1 all in stock

    """
    # get initial weightings
    if mw is None:
        W = np.ones(n) / n
    else:
        W = mw

    # R is the vector of expected returns
    R = expected_returns
    # C is the covariance matrix
    C = sk_co_var

    market_return = compute_mean(W, R)
    market_variance = compute_var(W, C)

    # Compute implied equity risk premium
    delta = (market_return - risk_free) / market_variance
    # Compute equilibrium excess returns
    Pi = dot(dot(delta, C), W)

    # Solve for weights before incorporating views
    W = solve_weights(Pi + risk_free, C, risk_free, allocation, assets_type,
                      constrains, initial_w, order)

    if views:
        # calculate tangency portfolio
        _mean, var = compute_mean_var(W, R, C)
        # Compute implied equity risk premium
        delta = (_mean - risk_free) / var
        # Compute equilibrium excess returns
        Pi = dot(dot(delta, C), W)
        # VIEWS ON ASSET
        P = np.array(views)
        Q = np.array(qs)

        # omega represents
        # the uncertainty of our views. Rather than specify the 'confidence'
        # in one's view explicitly, we extrapolate an implied uncertainty
        # from market parameters.
        omega = dot(dot(dot(tau, P), C), transpose(P))

        # Compute equilibrium excess returns taking into
        # account views on assets
        sub_a = inv(dot(tau, C))
        sub_b = dot(dot(transpose(P), inv(omega)), P)
        sub_c = dot(inv(dot(tau, C)), Pi)
        sub_d = dot(dot(transpose(P), inv(omega)), Q)
        Pi_new = dot(inv(sub_a + sub_b), (sub_c + sub_d))
        new_weights = solve_weights(Pi_new + risk_free, C, risk_free,
                                    allocation, assets_type, constrains, W,
                                    order)
        new_weights = np.around(new_weights, decimals=2)
    else:
        new_weights = np.around(W, decimals=2)

    # normalize weights
    # remove weights < 5%
    # for i in range(len(new_weights)):
    #    if new_weights[i] < 0.05:
    #        new_weights[i] = 0

    _mean, var = compute_mean_var(new_weights, expected_returns, co_vars)
    return new_weights, _mean, var


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


def markowitz_optimizer(mu, sigma, lam=1):
    '''
    Implementation of a long only mean-variance optimizer
        based on Markowitz's Portfolio
    Construction method:

    https://en.wikipedia.org/wiki/Modern_portfolio_theory

    This function relies on cvxpy.

    Argument Definitions:
    mu    -- 1xn numpy array of expected asset returns
    sigma -- nxn covariance matrix between asset return time series
    lam   -- optional risk tolerance parameter

    Argument Constraints:
    mu    -- expected return bector
    sigma -- positive semidefinite symmetric matrix
    lam   -- any non-negative float
    '''

    # define variable of weights to be solved for by optimizer
    x = Variable(len(sigma))
    # define Markowitz mean/variance objective function
    objective = Minimize(quad_form(x, sigma) - lam * mu * x)
    constraints = [sum_entries(x) == 1, x >= 0]  # define long only constraint
    p = Problem(objective, constraints)  # create optimization problem
    L = p.solve()  # solve problem
    return np.array(x.value).flatten()  # return optimal weights


def markowitz_optimizer_2(mu, sigma, m, alpha, lam=1):
    """
    Implementation of a long only mean-variance optimizer based
        on Markowitz's Portfolio
    Construction method:

    https://en.wikipedia.org/wiki/Modern_portfolio_theory

    This function relies on cvxpy.

    Argument Definitions:
    :param mu: 1xn numpy array of expected asset returns
    :param sigma: nxn covariance matrix between asset return time series
    :param m: first m
    :param alpha: percentage of portfolio weight to place in the first m assets
             note that 1-alpha percent of the portfolio weight will be placed
             in (m+1)st through nth asset
    :param lam: optional risk tolerance parameter

    Argument Constraints:
    sigma -- positive semidefinite symmetric matrix
    m     -- m < n
    alpha -- a float between 0 and 1
    lam   -- any non-negative float
    """

    # define variable of weights to be solved for by optimizer
    x = Variable(len(sigma))
    # define Markowitz mean/variance objective function
    objective = Minimize(quad_form(x, sigma) - lam * mu * x)
    constraints = [sum_entries(x[0:m]) == alpha,
                   sum_entries(x[m::]) == (1 - alpha),
                   x >= 0]  # define long only constraint
    p = Problem(objective, constraints)  # create optimization problem
    L = p.solve()  # solve problem
    return np.array(x.value).flatten()  # return optimal weights


def markowitz_optimizer_3(xs, sigma, lam, mu, constraints):
    """
    Optimise against a set of pre-constructed constraints
    :param xs: The variables to optimise
    :param sigma: nxn covariance matrix between asset return time series
    :param lam: Risk tolerance factor
    :param mu: 1xn numpy array of expected asset returns
    :param constraints: List of constrains to optimise with respect to.
    :return: (weights, cost)
             - weights: The calculated weight vector of each asset
             - cost: The total cost of this portfolio.
                     Useful for ranking optimisation outputs
    """
    # define Markowitz mean/variance objective function
    objective = Minimize(quad_form(xs, sigma) - lam * mu * xs)
    p = Problem(objective, constraints)  # create optimization problem
    res = p.solve()  # solve problem
    # If it was not solvable, fail
    if type(res) == str:
        raise OptimizationFailed(res)

    if xs.get_data()[0] == 1:
        weights = np.array([[xs.value]])
    else:
        weights = np.array(xs.value).T

    if weights.any():
        return weights[0], res  # return optimal weights and the cost.
    else:
        return weights, res


def markowitz_cost(ws, sigma, lam, mu):
    """
    Calculate the markowitz cost of a particular portfolio configuration
    :param ws: A 1xn numpy array of the weights of each asset.
    :param sigma: nxn covariance matrix between asset return time series
    :param lam: Risk tolerance factor
    :param mu: 1xn numpy array of expected asset returns
    :return: The cost of this particular configuration
    real(x'*Q*x) or x'*((Q+Q'/2))*x
    """
    return (ws.dot(sigma).dot(ws.T).real - np.dot(lam, mu).dot(ws.T))[0, 0]
