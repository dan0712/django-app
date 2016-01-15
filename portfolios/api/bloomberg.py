import datetime
import logging
from gzip import decompress
from time import sleep

import pysftp
import pandas as pd
from io import StringIO

# TODO: Remove this hackery
hn = 'dlsftp.bloomberg.com'
un = 'dl788259'
pw = '+gT[zfV9Bu]Ms.4'

logger = logging.getLogger("bloomberg_api")

class BloombergApi(object):
    _opening_stanza = 'START-OF-FILE\n'
    _closing_stanza = '\nEND-OF-FILE\n'
    _start_of_fields = '\nSTART-OF-FIELDS\n'
    _end_of_fields = '\nEND-OF-FIELDS\n'
    _start_of_data = 'START-OF-DATA\n'
    _end_of_data = '\nEND-OF-DATA\n'

    def __init__(self, host, username, password):
        self._tstr = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self._request_id = 0
        self._host = host
        self._username = username
        self._password = password

    def _build_header(self, headers):
        self._request_id += 1
        rid = 'bbpy_{}_{}'.format(self._tstr, self._request_id)
        header = '''
            FIRMNAME={}
            REPLYFILENAME={}.dat
            COMPRESS=yes
            PROGRAMFLAG=oneshot
        '''.format(self._username, rid)

        return rid, header + '\n'.join('{}={}'.format(key, val) for key, val in headers.items())

    def _build_fields(self, fields):
        return self._start_of_fields + '\n'.join(fields) + self._end_of_fields

    def _build_data(self, data):
        return self._start_of_data + '\n'.join(data) + self._end_of_data

    def build_request(self, headers, fields, data):
        """

        :param headers: A dict with the header options to set
        :param fields: A list of the fields we want
        :param data: A list of the lines for the data section.
        :return: (rid, request)
                    - rid is the identifier of the request
                    - request is the request text.
        """
        rid, hdrs = self._build_header(headers)
        return rid, ''.join([self._opening_stanza,
                             hdrs,
                             self._build_fields(fields),
                             self._build_data(data),
                             self._closing_stanza])

    def send_request(self, sftp, rid, request):
        """
        Submits a request to the sftp server
        :param sftp: A connection to the Bloomberg (s)ftp server directory.
        :param rid: The request id for this request.
        :param request: A formatted request for bloomberg.
        """
        with sftp.open('{}.req'.format(rid), mode='w') as request_file:
            request_file.write(request)
            logger.info('Submitted request id: {} to Bloomberg sftp server'.format(rid))

    def get_response(self, sftp, rid, responses):
        replyname = '{}.dat.gz'.format(rid)
        if sftp.exists(replyname):
            with sftp.open(replyname) as replyfile:
                responses[rid] = decompress(replyfile.read()).decode("utf-8")
            return True
        # Response not ready so return false.
        return False

    def request(self, requests):
        """
        Make a synchronous request using the sftp service. Waits until a response is available for all requests.
        :param requests: A dict from request id to the request text for all the requests we want to process.
        :return: A dict from request id to response contents
        """
        # TODO: Handle failure cases
        responses = {}
        with pysftp.Connection(self._host, username=self._username, password=self._password) as sftp:
            # Send each request in the collection to Bloomberg, and wait until they are all done.
            pending = []
            for rid, request in requests.items():
                self.send_request(sftp, rid, request)
                pending.append(rid)

            while len(pending) > 0:
                sleep(60)
                pending = [rid for rid in pending if not self.get_response(sftp, rid, responses)]
                assert len(pending) + len(responses) == len(requests)

        return responses

    def parse_hist_security_response(self, response, begin_date, end_date, fields):
        in_sec = False
        dframes = {}
        for line in StringIO(response):
            bits = line.split('|', 4)
            if in_sec:
                if bits[0] == 'END SECURITY':
                    in_sec = False
                    ret_code = int(bits[3])
                    if ret_code != 0:
                        estr = "Received return code: {} for history request for security: {}"
                        logger.warn(estr.format(ret_code, sec))
                else:
                    assert bits[0] == sec
                    try:
                        val = float(bits[2])
                    except ValueError:
                        val = None
                        logger.debug("Could not convert val: {} to float".format(bits[2]))
                    if val:
                        dframe.loc[datetime.datetime.strptime(bits[1], '%d/%m/%Y'), col] = val

            elif bits[0] == 'START SECURITY':
                in_sec = True
                sec = bits[1]
                col = bits[2]
                if sec in dframes:
                    dframe = dframes[sec]
                else:
                    dframe = pd.DataFrame(index=pd.date_range(begin_date, end_date), columns=fields)
                    dframes[sec] = dframe

        return dframes


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

    if end_date == None:
        end_date = begin_date

    api = BloombergApi(hn, un, pw)
    hrid, hist_req = api.build_request(hist_headers, hist_fields, ids)
    responses = api.request({hrid: hist_req})
    dframes = api.parse_hist_security_response(responses[hrid], begin_date, end_date, hist_fields)
    oframe = pd.DataFrame(index=pd.date_range(begin_date, end_date))
    for id, fr in dframes.items():
        oframe[id.split()[0]] = fr['PX_MID']

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

    hist_fields = ['FUND_NET_ASSET_VAL',
                   'FUND_TOTAL_ASSETS']

    '''
        Other fund-applicable history fields that may be of interest in the future:
        DVD_SH_LAST
        PX_OPEN
        PX_HIGH
        PX_LOW
        PX_LAST
        PX_MID
        PX_VOLUME
    '''

    api = BloombergApi(hn, un, pw)
    hrid, hist_req = api.build_request(hist_headers, hist_fields, ids)
    responses = api.request({hrid: hist_req})

    dframes = api.parse_hist_security_response(responses[hrid], begin_date, end_date, hist_fields)
    # FUND_TOTAL_ASSETS is in million of asset currency. Convert it to base qty.
    for frame in dframes.values():
        frame.dropna(how='all', inplace=True)
        frame['FUND_TOTAL_ASSETS'] *= 1000000
        frame.columns = ['nav', 'aum']

    return dframes
