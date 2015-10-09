__author__ = 'cristian'
import urllib.request
from datetime import datetime
import pandas as pd
from pandas import Series
import json
from main.models import DataApiDict, MonthlyPrices
from urllib.parse import quote
import calendar
from bs4 import BeautifulSoup
from portfolios.models import MarketCap


class YahooApi:
    currency_cache = {"AUD": 1}

    symbol_dict = None
    google_dict = None
    dates = None

    def __init__(self):
        today = datetime.today()
        self.today_year = today.year
        self.today_month = today.month - 1
        self.today_day = today.day

        self.symbol_dict = {}
        self.google_dict = {}

        for dad in DataApiDict.objects.filter(api="YAHOO").all():
            self.symbol_dict[dad.platform_symbol] = dad.api_symbol

        for dad in DataApiDict.objects.filter(api="GOOGLE").all():
            self.google_dict[dad.platform_symbol] = dad.api_symbol

    def get_all_prices(self, ticker_symbol, period="m"):
        if period == "m":
            self.dates = pd.date_range('2010-01-01', '{0}-{1}-01'
                                       .format(self.today_year, self.today_month+1), freq='M')
        elif period == "d":
            self.dates = pd.date_range('2010-01-01', '{0}-{1}-{2}'
                                       .format(self.today_year, self.today_month+1, self.today_day), freq='D')

        db_symbol = ticker_symbol
        ticker_symbol = self.symbol_dict.get(ticker_symbol, ticker_symbol)
        url = "http://real-chart.finance.yahoo.com/table.csv?s=%s&a=00&b=01&c=2010&d=%02d&e=%02d&f=%d&g=%s" \
              "&ignore=.csv" % (quote(ticker_symbol), self.today_month, self.today_day, self.today_year, period)

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
                        last_day = calendar.monthrange(int(d_items[0]), int(d_items[1]))[1]
                        cells[0] += "-" + str(last_day)
                        date = cells[0]
                    else:
                        date = cells[0]
                    close = float(cells[4])
                    price_data[pd.to_datetime(date)] = close
        except urllib.request.HTTPError as e:
            raise Exception("{0} : {1}".format(e.msg, url))

        if period == "m":
            for date, price in price_data.items():
                mp, is_new = MonthlyPrices.objects.get_or_create(date=date, symbol=db_symbol)
                mp.price = price
                mp.save()
        return Series(price_data, index=self.dates, name=db_symbol)

    def to_aud(self, currency):
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
 
    def market_cap(self, ticker):
        ticker_symbol = self.symbol_dict.get(ticker.symbol, ticker.symbol)
        url = "http://finance.yahoo.com/q?s={0}".format(ticker_symbol)
        with urllib.request.urlopen(url) as response:
            soup = BeautifulSoup(response)
            net_asset = soup.select('#table1 > tr:nth-of-type(6) > td')[0].getText()
            if "B" in net_asset:
                cap = float(net_asset.replace("B", ""))*1000
            elif "M" in net_asset:
                cap = float(net_asset.replace("M", ""))
            else:
                cap = 0
        value = cap*self.to_aud(ticker.currency)
        mp, is_new = MarketCap.objects.get_or_create(ticker=ticker)
        mp.value = value
        mp.save()
        return value
   
class DbApi:

    dates = None

    def __init__(self):
        today = datetime.today()
        self.today_year = today.year
        self.today_month = today.month - 1
        self.today_day = today.day

    def get_all_prices(self, ticker_symbol):
        self.dates = pd.date_range('2010-01', '{0}-{1}'
                                   .format(self.today_year, self.today_month+1), freq='M')

        prices = MonthlyPrices.objects.filter(symbol=ticker_symbol).all()
        price_data = {}

        for i in prices:
            price_data[pd.to_datetime(i.date.strftime("%Y-%m-%d"))] = i.price
        return Series(price_data, index=self.dates, name=ticker_symbol)

    def market_cap(self, ticker):
        mp = MarketCap.objects.get(ticker=ticker) 
        return mp.value
   

