__author__ = 'cristian'

import scipy.optimize
from numpy import array, zeros


def min_drift_wdw(shares_change, current_shares, tickers_price, target_allocation):
    new_shares = current_shares - shares_change
    total_balance = sum(new_shares * tickers_price)
    current_allocation = (new_shares * tickers_price) / total_balance
    drift = sum(abs(current_allocation - target_allocation))
    return drift * 100


def min_drift_deposit(shares_change, current_shares, tickers_price, target_allocation):
    new_shares = current_shares + shares_change
    total_balance = sum(new_shares * tickers_price)
    current_allocation = (new_shares * tickers_price) / total_balance
    drift = sum(abs(current_allocation - target_allocation))

    return drift * 100


def solve_shares_wdw(current_shares, tickers_price, target_allocation, amount):
    current_shares = array(current_shares)
    tickers_price = array(tickers_price)
    target_allocation = array(target_allocation)

    n = len(current_shares)
    shares_change = zeros([n])

    # Bounds for decision variables
    b_ = [(0, float("{:.2f}".format(current_shares[i]))) for i in range(n)]

    # Constraints - weights must sum to 1
    # sum of weights of stock should be equal to allocation
    c_ = ({'type': 'eq', 'fun': lambda x: abs(sum(x * tickers_price)) - amount})

    # 'target' return is the expected return on the market portfolio
    optimized = scipy.optimize.minimize(min_drift_wdw, shares_change,
                                        (current_shares, tickers_price, target_allocation),
                                        method='SLSQP', constraints=c_, bounds=b_, options={"maxiter": 1000})
    if not optimized.success:
        raise BaseException(optimized.message)
    return list(optimized.x)


def solve_shares_deposit(current_shares, tickers_price, target_allocation, amount):
    current_shares = array(current_shares)
    tickers_price = array(tickers_price)
    target_allocation = array(target_allocation)

    n = len(current_shares)
    shares_change = [amount / n / tickers_price[i] for i in range(n)]

    # Bounds for decision variables
    b_ = [(0, amount / tickers_price[i]) for i in range(n)]

    # Constraints - weights must sum to 1
    # sum of weights of stock should be equal to allocation
    c_ = ({'type': 'eq', 'fun': lambda x: abs(sum(x * tickers_price)) - amount})

    # 'target' return is the expected return on the market portfolio
    optimized = scipy.optimize.minimize(min_drift_deposit, shares_change, (current_shares, tickers_price,
                                                                           target_allocation),
                                        method='SLSQP', constraints=c_, bounds=b_, options={"maxiter": 1000})
    if not optimized.success:
        raise BaseException(optimized.message)
    return list(optimized.x)


def solve_shares_re_balance(current_shares, tickers_price, target_allocation):
    current_shares = array(current_shares)
    tickers_price = array(tickers_price)
    target_allocation = array(target_allocation)

    total_balance = sum(current_shares * tickers_price)
    target_share_values = total_balance * target_allocation
    new_shares = target_share_values / tickers_price

    return new_shares - current_shares
