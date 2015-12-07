import pandas as pd 
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Yahoo_Data'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'BL_model'))
from yahoo_downloader import download_data
from bl_model import bl_model

import numpy as np 
import numpy.linalg as la 
from cvxpy import Variable, Minimize, quad_form, Problem, sum_entries, norm

## Get satellite data
df = pd.read_csv('Active_Fund_Prices.csv')
df = df.set_index(pd.DatetimeIndex(df['Date'])).dropna()
df = df.drop('Date',1)
satrtndf = df.pct_change(1)

## Get core data 
yahoo_tkrlst = ['VAS.AX','VLC.AX','VSO.AX','VHY.AX','BOND.AX'] 
start_date = '2010-4-10'
end_date = '2015-11-24'
rtndf = download_data(yahoo_tkrlst, start_date, end_date)  # daily return dataframe 
rtndf = rtndf.set_index(pd.DatetimeIndex(rtndf.index)).dropna()

## Combine Dataframes
fdf = pd.concat([rtndf,satrtndf],axis=1).dropna()

muvec = (fdf.cumsum().ix[-1,:]/len(fdf)).values
covmat = np.array(fdf.cov())

def core_sat_optimizer(mu, sigma, m1, m2, alpha1, alpha2, lam = 1):

    x = Variable(len(sigma))   # define variable of weights to be solved for by optimizer 
    objective = Minimize(quad_form(x,sigma)-lam*mu*x) # define Markowitz mean/variance objective function 
    constraints = [sum_entries(x[0:m1])==alpha1, sum_entries(x[m1:m1+m2])==alpha2, sum_entries(x[m1+m2::])==(1-alpha1-alpha2), x>=0] # define long only constraint
    p = Problem(objective, constraints)     # create optimization problem  
    L = p.solve()                           # solve problem 
    return np.array(x.value).flatten()      # return optimal weights 


wopt = core_sat_optimizer(muvec,covmat,4,1,0.2,0.4)
print wopt 

