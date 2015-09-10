__author__ = 'cristian'

from numpy import matrix, array, zeros, empty, sqrt, ones, dot, append, mean, cov, transpose, linspace
from numpy.linalg import inv, pinv
import numpy as np
import scipy.optimize
import math
import functools

# This algorithm pecontext.rforms a Black-Litterman portfolio construction. The framework
# is built on the classical mean-variance approach, but allows the investor to
# specify views about the over- or under- pecontext.rformance of various assets.
# Uses ideas from the Global Minimum Variance Portfolio
# algorithm posted on Quantopian. Ideas also adopted from
# http://www.quantandfinancial.com/2013/08/portfolio-optimization-ii-black.html.

# window gives the number of data points that are extracted from historical data
# to estimate the expected returns and covariance matrix.
window = 255
refresh_rate = 40


# Compute the expected return of the portfolio.
def compute_mean(W, R):
    return sum(R*W)


# Compute the variance of the portfolio.
def compute_var(W,C):
    return dot(dot(W, C), W)


# Combination of the two functions above - mean and variance of returns calculation.
def compute_mean_var(W, R, C):
    return compute_mean(W, R), compute_var(W, C)


def fitness(W, R, C, r):
    # For given level of return r, find weights which minimizes portfolio variance.
    mean_1, var = compute_mean_var(W, R, C)
    # Penalty for not meeting stated portfolio return effectively serves as optimization constraint
    # Here, r is the 'target' return
    penalty = 0.1*abs(mean_1-r)
    return var + penalty


# Solve for optimal portfolio weights
def solve_weights(R, C, rf):
    n = len(R)
    W = ones([n])/n # Start optimization with equal weights
    b_ = [(0.1, 1) for i in range(n)] # Bounds for decision variables
    c_ = ({'type': 'eq', 'fun': lambda W: sum(W)-1.}) # Constraints - weights must sum to 1
    # 'target' return is the expected return on the market portfolio
    optimized = scipy.optimize.minimize(fitness, W, (R, C, sum(R*W)), method='SLSQP', constraints=c_, bounds=b_)
    if not optimized.success:
        raise BaseException(optimized.message)
    return optimized.x


# Weights - array of asset weights (derived from market capitalizations)
# Expreturns - expected returns based on historical data
# Covars - covariance matrix of asset returns based on historical data
def assets_meanvar(daily_returns):

    # Calculate expected returns
    expreturns = array([])
    (rows, cols) = daily_returns.shape
    for r in range(rows):
        expreturns = append(expreturns, mean(daily_returns[r]))

    # Compute covariance matrix
    covars = cov(daily_returns)
    # Annualize expected returns and covariances
    # Assumes 255 trading days per year
    expreturns = (1+expreturns)**255-1
    covars = covars * 255

    return expreturns, covars


def handle_data(all_prices, risk_free, allocation, asset_type):
    """
    all prices: table with the dayle closed price for each asset
    risk_free: risk free rate
    asset_type: list (0,0,0,1,1,1), where 1 means that is a stock and 0 that is a bond
    """

    # get initial weightings
    W = np.ones()/n

    # Drop missing values and transpose matrix
    daily_returns = all_prices.pct_change().dropna().values.T

    expected_returns, co_vars = assets_meanvar(daily_returns)

    # R is the vector of expected returns
    R = expected_returns
    # C is the covariance matrix
    C = co_vars

    new_mean = compute_mean(W, R)
    new_var = compute_var(W, C)

    # Compute implied equity risk premium
    lmb = (new_mean - risk_free) / new_var
    # Compute equilibrium excess returns
    Pi = dot(dot(lmb, C), W)

    # Solve for weights before incorporating views
    W = solve_weights(Pi+risk_free, C, risk_free, allocation)

    print(W)

    # calculate tangency portfolio
    mean, var = compute_mean_var(W, R, C)

    """
    # VIEWS ON ASSET PEcontext.rfORMANCE
    # Here, we give two views, that Google will outpecontext.rform Apple by 3%, and
    # that Google will outpecontext.rform Microsoft by 2%.
    P = np.array([[1,-1,0,0], [1,0,-1,0]])
    Q = np.array([0.03,0.02])

    omega = dot(dot(dot(context.tau, P), C), transpose(P)) # omega represents
    # the uncertainty of our views. Rather than specify the 'confidence'
    # in one's view explicitly, we extrapolate an implied uncertainty
    # from market parameters.

    # Compute equilibrium excess returns taking into account views on assets
    sub_a = inv(dot(context.tau, C))
    sub_b = dot(dot(transpose(P), inv(omega)), P)
    sub_c = dot(inv(dot(context.tau, C)), Pi)
    sub_d = dot(dot(transpose(P), inv(omega)), Q)
    Pi_new = dot(inv(sub_a + sub_b), (sub_c + sub_d))
    # Pecontext.rform a mean-variance optimization taking into account views

    new_weights = solve_weights(Pi_new + context.rf, C, context.rf)

    leverage = sum(abs(new_weights))
    portfolio_value = (context.portfolio.positions_value + context.portfolio.cash)/leverage

    # Re-weight portfolio
    security_index = 0
    for security in context.securities:
        current_position = context.portfolio.positions[security].amount
        new_position = (portfolio_value*new_weights[security_index])/all_prices[security][window-1]
        order(security, new_position-current_position)
        security_index += security_index
    context.day += context.day
    """