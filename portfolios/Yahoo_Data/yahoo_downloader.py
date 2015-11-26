import pandas as pd
import os 
from urllib import urlretrieve

def _build_url(tkr, start_date, end_date):
    ''' 
    This function builds a url to download a csv file from yahoo finance 

    Argument Definitions:
    tkr -- yahoo finance security ticker name, e.g. 'IBM' 
    start_date  -- starting date string, e.g. '2010-4-10' 
    end_date -- ending date string, e.g. '2015-11-24'
    '''
    sY, sM, sD = start_date.split('-')
    eY, eM, eD = end_date.split('-')
    sM = str(int(sM) - 1)
    eM = str(int(eM) - 1)

    url = "http://real-chart.finance.yahoo.com/table.csv?s="+tkr+"&a="+sM+"&b="+ \
    sD+"&c="+sY+"&d="+eM+"&e"+eD+"&f="+eY+"&g=d&ignore=.csv"

    return url

def download_data(tkrlst, start_date, end_date, rtn_flag=True):
    ''' 
    Function to download closing prices from yahoo finance.  Returns a pandas dataframe of
    the data 

    Argument Definitions: 
    tkrlst -- list of tickers for which one wants closing prices
    start_date -- starting date for data 
    end_date -- ending date for data 
    '''
    dflst = []
    prcdf = pd.DataFrame()
    fdf = pd.DataFrame()
    tmppath = os.path.join(os.path.dirname(__file__), 'Tmp/tmpdat.csv')

    for tkr in tkrlst:
        url = _build_url(tkr, start_date, end_date)
        csvfle = urlretrieve(url, tmppath)
        dflst.append(pd.read_csv(tmppath)[['Date','Close']])

    for df in dflst: 
        tmpdf = df.set_index('Date')
        prcdf = pd.concat([prcdf,tmpdf],axis=1)

        if rtn_flag:
            tmprtndf = ((tmpdf-tmpdf.shift(1))/tmpdf)
            fdf = pd.concat([fdf,tmprtndf],axis=1)
        else: 
            fdf = prcdf

    fdf.columns = tkrlst
    
    return fdf

