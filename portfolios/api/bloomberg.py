import gzip
import os

import pandas as pd
from bberg.sftp import Sftp as BbSftp, parse_hist_security_response

# TODO: Remove this hackery
hn = 'dlsftp.bloomberg.com'
un = 'dl788259'
pw = '+gT[zfV9Bu]Ms.4'


def get_fx_rates(pairs, begin_date, end_date=None):
    '''

    :param pairs: list of (str, str) tuples indicating the fx pairs desired.
    :param begin_date: begin datetime.date object inclusive for data to download
    :param end_date: end datetime.date object inclusive for data to download. If not specified, assumed same as begin_date.
    :return: Pandas date series dataframe with column names of fx pair "AUDUSD" for example,
             entries being the rate from first to second.
    '''
    hist_headers = {'PROGRAMNAME': 'gethistory',
                    'DATERANGE': '{}|{}'.format(begin_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')),
                    'DATEFORMAT': 'ddmmyyyy'}

    hist_fields = ['PX_MID']

    ids = ['{}{} Curncy'.format(a, b) for a, b in pairs]

    if end_date is None:
        end_date = begin_date

    api = BbSftp(hn, un, pw)
    hrid, hist_req = api.build_request(hist_headers, hist_fields, ids)
    responses = api.request({hrid: hist_req})
    dframes = parse_hist_security_response(responses[hrid], begin_date, end_date, hist_fields)
    oframe = pd.DataFrame(index=pd.date_range(begin_date, end_date))
    for iid in ids:
        oframe[iid.split()[0]] = dframes[iid]['PX_MID']

    return oframe


def get_fund_hist_data(ids, begin_date, end_date):
    """

    :param ids: A list of bloomberg identification strings "<ticker> [<pricing source>] <market sector>" for each fund
                you want to retrieve data for.
    :param begin_date: begin datetime.date object inclusive for data to download
    :param end_date: end datetime.date object inclusive for data to download. If not specified, assumed same as begin_date.
    :return: Dict from input id to Pandas date series DataFrame with column names and types as follows:
             nav: float
             aum: int
    """

    '''
    Other things we may return in future:
             mic: str (the market identifier that the bid/ask/spread info is from)
             bid_open: float
             bid_high: float
             bid_low: float
             bid_close: float
             ask_open: float
             ask_high: float
             ask_low: float
             ask_close: float
             spread_open: float
             spread_high: float
             spread_low: float
             spread_close: float
             volume: int (is this for a market or across all markets??)
             expense_ratio: float
             dividend: float

    '''
    ref_headers = {'PROGRAMNAME': 'getdata',
                   'COLUMNHEADER': 'yes',
                   'DATEFORMAT': 'ddmmyyyy'}

    ref_fields = ['CRNCY',
                  'FUND_EXPENSE_RATIO',
                  'DVD_CRNCY',
                  'DVD_RECORD_DT',
                  'AVERAGE_BID_ASK_SPREAD_%']

    hist_headers = {'PROGRAMNAME': 'gethistory',
                    'DATERANGE': '{}|{}'.format(begin_date.strftime('%Y%m%d'),
                                                end_date.strftime('%Y%m%d')),
                    'DATEFORMAT': 'ddmmyyyy'}

    hist_fields = ['PX_LAST',
                   'FUND_TOTAL_ASSETS',
                   'PX_MID',
                   'PX_HIGH',
                   'PX_LOW',
                   'FUND_NET_ASSET_VAL']

    '''
        Other fund-applicable history fields that may be of interest in the future:
        FUND_NET_ASSET_VAL
        DVD_SH_LAST
        PX_OPEN
        PX_HIGH
        PX_LOW
        PX_LAST
        PX_MID
        PX_VOLUME
    '''
    use_id = os.getenv('BBERG_HIST_FILE')
    if use_id is None:
        api = BbSftp(hn, un, pw)
        hrid, hist_req = api.build_request(hist_headers, hist_fields, ids)
        print("Using request id: {}".format(hrid))
        responses = api.request({hrid: hist_req})
        response = responses[hrid]
    else:
        with gzip.open(use_id) as hist_file:
            response = hist_file.read().decode("utf-8")
    dframes = parse_hist_security_response(response, begin_date, end_date, hist_fields)

    def price_getter(row):
        h = row['PX_HIGH']
        l = row['PX_LOW']
        m = row['PX_MID']
        la = row['PX_LAST']
        return (h + l) / 2 if (pd.notnull(h) and pd.notnull(l)) else (m if pd.notnull(m) else (la if pd.notnull(la) else row['FUND_NET_ASSET_VAL']))

    for key, frame in dframes.items():
        frame.dropna(how='all', inplace=True)
        # FUND_TOTAL_ASSETS is in million of asset currency. Convert it to base qty.
        frame['FUND_TOTAL_ASSETS'] *= 1000000
        nprices = frame.apply(price_getter, axis=1)
        if not nprices.empty:
            frame['nav'] = nprices
            #frame.to_csv("/tmp/bberg_{}.csv".format(key))
            frame.iloc[:, 0] = nprices
        frame.drop(frame.columns[2:], axis=1, inplace=True)  # Remove the cols we don't want.
        frame.columns = ['nav', 'aum']

    return dframes
