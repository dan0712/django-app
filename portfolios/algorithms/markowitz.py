import numpy as np
from cvxpy import Variable, Minimize, quad_form, sum_entries, Problem
import cvxpy

from portfolios.exceptions import OptimizationFailed


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
    data = p.get_problem_data(cvxpy.ECOS)
    res = p.solve(verbose=True)  # solve problem
    # If it was not solvable, fail
    if type(res) == str:
        raise OptimizationFailed(res + 'get_problem_data:' + str(data))

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