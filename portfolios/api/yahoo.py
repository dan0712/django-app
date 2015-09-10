__author__ = 'cristian'
import urllib.request
from datetime import datetime
import pandas as pd
from pandas import Series
import json


class YahooApi:

    symbol_dict = {"VSO": "VSO.AX",
                   "VHY": "VHY.AX",
                   "VGS": "VGS.AX",
                   "VLC": "VLC.AX",
                   "VAS": "VAS.AX",
                   "BOND": "BOND.AX",
                   "RGB": "RGB.AX",
                   "ILB": "ILB.AX",
                   "RSM": "RSM.AX"}

    def __init__(self):
        today = datetime.today()
        self.today_year = today.year
        self.today_month = today.month - 1
        self.today_day = today.day
        self.dates = pd.date_range('2010-01-01', '{0}-{1}-{2}'
                                   .format(self.today_year, self.today_month+1, self.today_day), freq='D')

    def get_all_prices(self, ticker_symbol):

        ticker_symbol = self.symbol_dict.get(ticker_symbol, ticker_symbol)
        url = "http://real-chart.finance.yahoo.com/table.csv?s=%s&a=00&b=01&c=2010&d=%02d&e=%02d&f=%d&g=m" \
              "&ignore=.csv" % (ticker_symbol, self.today_month, self.today_day, self.today_year)
        price_data = {}
        with urllib.request.urlopen(url) as response:
            csv_file = response.read().decode("utf-8").splitlines()
            line_counter = 0
            for line in csv_file:
                if line_counter == 0:
                    line_counter += 1
                    continue
                cells = line.split(",")
                d_items = cells[0].split("-")
                cells[0] = d_items[0] + '-' + d_items[1]
                date = datetime.strptime(cells[0], "%Y-%m")
                close = float(cells[4])
                price_data[date] = close

        return Series(price_data, index=self.dates, name=ticker_symbol)

    @staticmethod
    def to_aud(currency):
        if currency == "AUD":
            return 1
        elif currency == "USD":
            url = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where' \
                  '%20symbol%20in%20(%22AUDUSD%3DX%22)%0A%09%09&format=json&diagnostics=true&' \
                  'env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback='
            with urllib.request.urlopen(url) as response:
                quote_json = json.loads(response.read().decode("utf-8"))
                bid = float(quote_json['query']['results']['quote']['Bid'])

            return bid

    def get_unit_price(self, ticker_symbol, currency):
        ticker_symbol = self.symbol_dict.get(ticker_symbol, ticker_symbol)

        url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance." \
              "quotes%20where%20symbol%20in%20(%22{0}%22)%0A%09%09&format=json&" \
              "diagnostics=true&env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback=".format(ticker_symbol)

        with urllib.request.urlopen(url) as response:
            quote_json = json.loads(response.read().decode("utf-8"))
            bid = quote_json['query']['results']['quote']['Bid']
            if bid is None:
                bid = quote_json['query']['results']['quote']['Ask']
            if bid is None:
                return None
            bid = float(bid)
        return bid*self.to_aud(currency)
