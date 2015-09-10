__author__ = 'cristian'

from numpy import  array, ones, dot, append, mean, cov, transpose
from numpy.linalg import inv
import numpy as np
import scipy.optimize


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
    return var - 0.1*mean_1 + penalty


# Solve for optimal portfolio weights
def solve_weights(R, C, risk_free, allocation, assets_type):
    n = len(R)
    W = ones([n])/n # Start optimization with equal weights

    b_ = [(0, 1) for i in range(n)] # Bounds for decision variables
    # Constraints - weights must sum to 1
    # sum of weights of stock should be equal to allocation
    c_ = ({'type': 'eq', 'fun': lambda W: sum(W)-1.},
          {'type': 'eq', 'fun': lambda W: dot(assets_type, W)-allocation})
    # 'target' return is the expected return on the market portfolio
    optimized = scipy.optimize.minimize(fitness, W, (R, C, sum(R*W)), method='SLSQP', constraints=c_, bounds=b_)
    if not optimized.success:
        raise BaseException(optimized.message)
    return optimized.x


# Weights - array of asset weights
# Expreturns - expected returns based on historical data
# Covars - covariance matrix of asset returns based on historical data
def assets_mean_var(monthly_returns):

    # Calculate expected returns
    expected_returns = array([])
    (rows, cols) = monthly_returns.shape
    for r in range(rows):
        expected_returns = append(expected_returns, mean(monthly_returns[r]))
    # Compute covariance matrix
    co_vars = cov(monthly_returns)
    # Annualized expected returns and covariances
    # Assumes 12 trading months per year
    expected_returns = (1+expected_returns)**12-1
    co_vars *= 12

    return expected_returns, co_vars


def handle_data(all_prices, risk_free, allocation, assets_type, views, qs, tau):
    """
    all prices: table with the monthly closed price for each asset
    risk_free: risk free rate
    asset_type: list (0,0,0,1,1,1), where 1 means that is a stock and 0 that is a bond
    allocation: number between 0-1, 0-means all in bond, 1 all in stock

    """
    n = all_prices.shape[1]
    # get initial weightings
    W = np.ones(n)/n

    # Drop missing values and transpose matrix
    monthly_returns = all_prices.pct_change().dropna().values.T
    expected_returns, co_vars = assets_mean_var(monthly_returns)

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
    W = solve_weights(Pi+risk_free, C, risk_free, allocation, assets_type)

    # calculate tangency portfolio
    mean, var = compute_mean_var(W, R, C)
    # Compute implied equity risk premium
    lmb = (mean - risk_free) / var
    # Compute equilibrium excess returns
    Pi = dot(dot(lmb, C), W)

    # VIEWS ON ASSET
    P = np.array(views)
    Q = np.array(qs)

    omega = dot(dot(dot(tau, P), C), transpose(P)) # omega represents
    # the uncertainty of our views. Rather than specify the 'confidence'
    # in one's view explicitly, we extrapolate an implied uncertainty
    # from market parameters.

    # Compute equilibrium excess returns taking into account views on assets
    sub_a = inv(dot(tau, C))
    sub_b = dot(dot(transpose(P), inv(omega)), P)
    sub_c = dot(inv(dot(tau, C)), Pi)
    sub_d = dot(dot(transpose(P), inv(omega)), Q)
    Pi_new = dot(inv(sub_a + sub_b), (sub_c + sub_d))
    new_weights = solve_weights(Pi_new+risk_free, C, risk_free, allocation, assets_type)
    _mean, var = compute_mean_var(W, R, C)

    return new_weights, _mean, var
