import numpy as np 
import numpy.linalg as la 
from cvxpy import Variable, Minimize, quad_form, Problem, sum_entries, norm

def bl_model(sigma, w_tilde, p, v, n, c=1, lambda_bar=1.2):
    '''
    This is an implementation of the Black-Litterman model based on Meucci's article: 

    http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1117574
 
    Argument Definitions: 
        Required:
        sigma -- nxn numpy array covariance matrix of the asset return time series   
        w_tilde -- 1xn numpy array market cap portfolio weights 
        p -- mxn numpy array corresponding to investor views on future asset movements  
        v -- 1xm numpy array of expected returns of portfolios corresponding to views  
        lambda_bar -- risk-aversion level which Black and Litterman set to 1.2
        n -- length of time series of returns used to compute covariance matrix 

        Optional:
        c -- constant representing overall confidence in the views 
        return estimator
        lambda_bar -- risk-aversion level which Black and Litterman set to 1.2
    
    Argument Constraints: 
        Required: 
        sigma -- positive definite symmetric matrix 
        w_tilde -- vector with positive entries that sum to one 
        p -- matrix of positive or negative floats  
        v -- matrix of positive or negative floats 

        Optional:
        c -- any positive float, default to 1 (as in example on page 5)
        lambda_bar -- positive float, default to 1.2 as mentioned after equation (5)
    '''

    pi = 2*lambda_bar*np.dot(sigma,w_tilde)  ## equation (5)
    tau = 1/float(n)  ## equation (8)

    omega = np.dot(np.dot(p,sigma),p.T)/c ## equation (12)

    ## Main model, equations (20) and (21)
    m1 = np.dot(tau*np.dot(sigma,p.T),la.inv(tau*np.dot(p,np.dot(sigma,p.T))+omega))
    m2 = v-np.dot(p,pi)
    m3 = np.dot(p,sigma)

    mu_BL = pi + np.dot(m1,m2)
    sig_BL  = (1+tau)*sigma - tau*np.dot(m1,m3)

    return mu_BL, sig_BL

def markowitz_optimizer(mu, sigma, lam = 1):
    '''
    Implementation of a long only mean-variance optimizer based on Markowitz's Portfolio
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

    x = Variable(len(sigma))   # define variable of weights to be solved for by optimizer 
    objective = Minimize(quad_form(x,sigma)-lam*mu*x) # define Markowitz mean/variance objective function 
    constraints = [sum_entries(x)==1, x>=0] # define long only constraint
    p = Problem(objective, constraints)     # create optimization problem  
    L = p.solve()                           # solve problem 
    return np.array(x.value).flatten()      # return optimal weights 

def markowitz_optimizer_2(mu, sigma, m, alpha, lam = 1):
    '''
    Implementation of a long only mean-variance optimizer based on Markowitz's Portfolio
    Construction method:

    https://en.wikipedia.org/wiki/Modern_portfolio_theory

    This function relies on cvxpy.

    Argument Definitions:
    mu    -- 1xn numpy array of expected asset returns 
    sigma -- nxn covariance matrix between asset return time series 
    m     -- first m  
    alpha -- percentage of portfolio weight to place in the first m assets
             note that 1-alpha percent of the portfolio weight will be placed 
             in (m+1)st through nth asset 
    lam   -- optional risk tolerance parameter 

    Argument Constraints: 
    mu    -- expected return bector 
    sigma -- positive semidefinite symmetric matrix 
    m     -- m < n
    alpha -- a float between 0 and 1
    lam   -- any non-negative float 
    '''

    x = Variable(len(sigma))   # define variable of weights to be solved for by optimizer 
    objective = Minimize(quad_form(x,sigma)-lam*mu*x) # define Markowitz mean/variance objective function 
    constraints = [sum_entries(x[0:m])==alpha, sum_entries(x[m::])==(1-alpha), x>=0] # define long only constraint
    p = Problem(objective, constraints)     # create optimization problem  
    L = p.solve()                           # solve problem 
    return np.array(x.value).flatten()      # return optimal weights 

