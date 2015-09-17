__author__ = 'cristian'
import urllib.request
from datetime import datetime
import pandas as pd
from pandas import Series
import json
from main.models import DataApiDict


class YahooApi:
    currency_cache = {"AUD": 1}

    symbol_dict = None
    google_dict = None

    def __init__(self):
        today = datetime.today()
        self.today_year = today.year
        self.today_month = today.month - 1
        self.today_day = today.day
        self.dates = pd.date_range('2010-01-01', '{0}-{1}-{2}'
                                   .format(self.today_year, self.today_month+1, self.today_day), freq='D')
        self.symbol_dict = {}
        self.google_dict = {}

        for dad in DataApiDict.objects.filter(api="YAHOO").all():
            self.symbol_dict[dad.platform_symbol] = dad.api_symbol

        for dad in DataApiDict.objects.filter(api="GOOGLE").all():
            self.google_dict[dad.platform_symbol] = dad.api_symbol

    def get_all_prices(self, ticker_symbol, period="m"):

        ticker_symbol = self.symbol_dict.get(ticker_symbol, ticker_symbol)
        url = "http://real-chart.finance.yahoo.com/table.csv?s=%s&a=00&b=01&c=2010&d=%02d&e=%02d&f=%d&g=%s" \
              "&ignore=.csv" % (ticker_symbol, self.today_month, self.today_day, self.today_year, period)
        price_data = {}
        try:
            with urllib.request.urlopen(url) as response:
                csv_file = response.read().decode("utf-8").splitlines()
                line_counter = 0
                for line in csv_file:
                    if line_counter == 0:
                        line_counter += 1
                        continue
                    cells = line.split(",")
                    d_items = cells[0].split("-")
                    if period == "m":
                        cells[0] = d_items[0] + '-' + d_items[1]
                        date = datetime.strptime(cells[0], "%Y-%m")
                    else:
                        date = datetime.strptime(cells[0], "%Y-%m-%d")
                    close = float(cells[4])
                    price_data[date] = close
        except urllib.request.HTTPError as e:
            raise Exception("{0} : {1}".format(e.msg, url))

        return Series(price_data, index=self.dates, name=ticker_symbol)

    def to_aud(self, currency: str)->float:
        if currency in self.currency_cache:
            return self.currency_cache[currency]
        ret = 1

        if currency == "USD":
            url = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where' \
                  '%20symbol%20in%20(%22AUDUSD%3DX%22)%0A%09%09&format=json&diagnostics=true&' \
                  'env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback='
            with urllib.request.urlopen(url) as response:
                quote_json = json.loads(response.read().decode("utf-8"))
                bid = float(quote_json['query']['results']['quote']['Bid'])

            ret = 1/bid

        if currency == "GBP":
            url = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where' \
                  '%20symbol%20in%20(%22GBPAUD%3DX%22)%0A%09%09&format=json&diagnostics=true&' \
                  'env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback='
            with urllib.request.urlopen(url) as response:
                quote_json = json.loads(response.read().decode("utf-8"))
                bid = float(quote_json['query']['results']['quote']['Bid'])

            ret = bid

        self.currency_cache[currency] = ret
        return ret

    def get_unit_price(self, ticker_symbol, currency):
        ticker_symbol = self.google_dict.get(ticker_symbol, ticker_symbol)

        url = "http://finance.google.com/finance/info?client=ig&q={}".format(ticker_symbol)
        with urllib.request.urlopen(url) as response:
            quote_json = json.loads(response.read().decode("utf-8", errors="ignore").replace("/", ""))
            bid = quote_json[0]['l']
            bid = float(bid)
        return bid*self.to_aud(currency)
