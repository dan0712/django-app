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



def initialize(context):

  # Set day
  context.day = 0

  context.rate = '1 Yr'

  context.tau = 0.025 # context.tau is a scalar indicating the uncertainty
  # in the CAPM (Capital Asset Pricing Model) prior

  context.rf = 0 # context.rf is the risk-free rate

  # Select five large cap equities for the portfolio
  context.securities = [sid(24),sid(26578),sid(3149), sid(5061)]
  # Apple, Google, GE, Microsoft
  context.market_cap = np.zeros(len(context.securities))
  context.cap_wts = np.array(len(context.securities))

  # Set Max and Min positions in security
  context.max_notional = 1000000.1
  context.min_notional = -1000000.0


def handle_data(context, data):
    # Compute market capitalizations and relative market weightings
    for i in range(0, len(context.securities)):
        if 'cap' in data[context.securities[i]]:
            context.market_cap[i] = data[context.securities[i]]['cap']
    total_cap = float(sum(context.market_cap))
    context.cap_wts = np.array(context.market_cap/total_cap)

    # Get historical prices
    all_prices = get_past_prices(data)
    if 'yield' in data['risk_free_rate']:
      context.rf = data['risk_free_rate']['yield']

    # Circuit breaker in case transform returns none
    if all_prices is None:
        return

    if context.day % refresh_rate is not 0:
        context.day = context.day + 1
        return
    # Make sure the columns of all_prices matches the order of
    # securites in context.securities.
    del all_prices['risk_free_rate']
    all_prices = all_prices[context.securities]
    # Drop missing values and transpose matrix
    daily_returns = all_prices.pct_change().dropna().values.T

    expreturns, covars = assets_meanvar(daily_returns)
    R = expreturns # R is the vector of expected returns
    C = covars # C is the covariance matrix
    W = context.cap_wts

    new_mean = compute_mean(W,R)
    new_var = compute_var(W, C)

    lmb = (new_mean - context.rf) / new_var # Compute implied equity risk premium
    Pi = dot(dot(lmb, C), W) # Compute equilibrium excess returns

    # Solve for weights before incorporating views
    W = solve_weights(Pi+context.rf, C, context.rf)

    mean, var = compute_mean_var(W, R, C) # calculate tangency portfolio

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