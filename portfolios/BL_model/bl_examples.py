from bl_model import bl_model, markowitz_optimizer 
import numpy as np 

## BL model (Meucci's version) 

volvec = [0.21, 0.24, 0.24, 0.25, 0.29, 0.31]
cormat = [[1., 0.54, 0.62, 0.25, 0.41, 0.59],
          [0.54, 1., 0.69, 0.29, 0.36, 0.83], 
          [0.62, 0.69, 1., 0.15, 0.46, 0.65],
          [0.25, 0.29, 0.15, 1., 0.47, 0.39],
          [0.41, 0.36, 0.46, 0.47, 1., 0.38],
          [0.59, 0.83, 0.65, 0.39, 0.38, 1.]]

# construct covariance matrix 
sigma = np.array(cormat)
for i in xrange(len(volvec)):
    for j in xrange(len(volvec)):
        sigma[i][j] = cormat[i][j]*volvec[i]*volvec[j]

# Let's write a function for the BL Model 
# We follow http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1117574

w_tilde = np.array([0.04, 0.04, 0.05, 0.08, 0.71, 0.08])
tau = 0.4
lambda_bar = 1.2

p = np.array([[0,1,0,0,0,0],[0,0,0,0,1,-1]])
v = [0.12, -0.1]
c = 1
n = 1/0.4 # just to match meucci's 

## Example 1 (problem given in paper)

mu, sig = bl_model(sigma, w_tilde, p, v, n)
wopt = markowitz_optimizer(mu,sig)

## Example 2 (demonstrate overwriting optional arguments) 

## Example 3 (no views ... using no views) 

