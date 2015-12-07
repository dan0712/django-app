from numpy import dot, cov, transpose, sqrt, isnan
from numpy.linalg import inv
import numpy as np
import scipy.optimize
from sklearn.covariance import OAS


def calculate_co_vars(assets_len, table):
    columns = list(table)
    sk = OAS(assume_centered=True)
    sk.fit(table.pct_change().dropna().values)

    # calculate covariance matrix
    co_vars = np.zeros([assets_len, assets_len])
    for i in range(assets_len):

        var_table = table.reindex(index=None, columns=[columns[i], columns[i]])
        monthly_returns_i_i = var_table.pct_change().dropna().values.T
        co_vars_i_i = assets_covariance(monthly_returns_i_i)
        co_vars[i, i] = co_vars_i_i[0, 1]

        for j in range(i+1, assets_len):
            # covariance
            new_table = table.reindex(index=None, columns=[columns[i], columns[j]])
            monthly_returns_i_j = new_table.pct_change().dropna().values.T
            co_vars_i_j = assets_covariance(monthly_returns_i_j)
            co_vars[j, i] = co_vars[i, j] = co_vars_i_j[0, 1]
    # annualized
    sk_co_var = ((1-sk.shrinkage_)*co_vars + sk.shrinkage_*np.trace(co_vars)/assets_len*np.identity(assets_len))
    return sk_co_var, co_vars


class OptimizationException(BaseException):
    pass


# Compute the expected return of the portfolio.
def compute_mean(W, R):
    return sum(R*W)


# Compute the variance of the portfolio.
def compute_var(W,C):
    return dot(dot(W, C), W)


def var_gradient(W, C):
    return dot(W, C) + dot(W, np.diag(np.diag(C))) 


# Combination of the two functions above - mean and variance of returns calculation.
def compute_mean_var(W, R, C):
    return compute_mean(W, R), compute_var(W, C)


def fitness(W, R, C, r, assets_type, allocation, constrains, iW, order, bonds):
    w_w = 10000
    w_er = 100
    w_sqrt = 100
    # For given level of return r, find weights which minimizes portfolio variance.
    mean_1, var = compute_mean_var(W, R, C)
    # Penalty for not meeting stated portfolio return effectively serves as optimization constraint
    # Here, r is the 'target' return
    jac = np.zeros(len(W))
    func = 0
    # expected returns function
    func = -w_er*mean_1
    # jac mean
    jac += -w_er*R

    # variance
    func += w_sqrt*sqrt(var)
    var_jac = var_gradient(W, C)/(2*sqrt(var))
    jac += w_sqrt*var_jac

    # ====================================================
    #               portfolio weights
    # ==================================================
    # 100% weight
    func += w_w*((sum(W)-1)**2)
    jac += w_w*(2*(sum(W) - 1) * np.ones(len(W)))

    # Allocation stock
    func += w_w*((dot(assets_type, W)-allocation)**2)
    jac += w_w*(2*(dot(assets_type, W)-allocation)*assets_type)
    bond_allocation = 1-allocation

    # Allocation bonds
    func += w_w*((dot(bonds, W)-bond_allocation)**2)
    jac += w_w*(2*(dot(bonds, W)-bond_allocation)*bonds)

    for ct in constrains:
        v, new_jac = ct(order, W)
        func += w_w*v
        jac += w_w*new_jac

    if (allocation != 0) and (allocation != 1):
        func += 10*sum((W-iW)**2)
        jac += 10*2*(W-iW)

    return np.around(func, decimals=10), np.around(jac, decimals=10)


# Solve for optimal portfolio weights
def solve_weights(R, C, risk_free, allocation, assets_type, constrains, iW, order):
    assets_type = np.array(assets_type)

    n = len(R)
    W = iW
    tol = 0.00001
    bonds = list(map(lambda x: 0 if x == 1 else 1, assets_type))
    bonds = np.array(bonds)
    b_ = [(0, 1) for i in range(n)] # Bounds for decision variables
    # Constraints - weights must sum to 1
    # sum of weights of stock should be equal to allocation
    # 'target' return is the expected return on the market portfolio
    optimized = scipy.optimize.minimize(fitness, W,
                                        (R, C, sum(R*W), assets_type, allocation, constrains, iW, order, bonds),
                                        jac=True, 
                                        method='SLSQP', bounds=b_, tol=tol,  options={"maxiter": 1000})
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
    asset_type: list (0,0,0,1,1,1), where 1 means that is a stock and 0 that is a bond
    allocation: number between 0-1, 0-means all in bond, 1 all in stock

    """
    # get initial weightings
    if mw is None:
        W = np.ones(n)/n
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
    W = solve_weights(Pi+risk_free, C, risk_free, allocation, assets_type, constrains, initial_w, order)

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

        # Compute equilibrium excess returns taking into account views on assets
        sub_a = inv(dot(tau, C))
        sub_b = dot(dot(transpose(P), inv(omega)), P)
        sub_c = dot(inv(dot(tau, C)), Pi)
        sub_d = dot(dot(transpose(P), inv(omega)), Q)
        Pi_new = dot(inv(sub_a + sub_b), (sub_c + sub_d))
        new_weights = solve_weights(Pi_new+risk_free, C, risk_free, allocation, assets_type, constrains, W, order)
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
