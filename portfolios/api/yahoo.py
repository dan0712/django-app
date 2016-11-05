import logging
import urllib.request
import datetime
import pandas as pd
from pandas import Series
import json

from main.management.commands.build_returns import get_price_returns
from main.models import DataApiDict, MarketCap
from urllib.parse import quote
import calendar
from bs4 import BeautifulSoup
import random
import scipy.interpolate
import time
import numpy as np
from dateutil.relativedelta import relativedelta

__author__ = 'cristian'

logger = logging.getLogger('yahoo_api')

'''
class YahooApi:
    currency_cache = {"AUD": 1}

    symbol_dict = None
    google_dict = None
    dates = None
    historical_currency_cache = dict()

    def __init__(self):
        today = datetime.today()
        self.today_year = today.year
        self.today_month = today.month - 1
        self.today_day = today.day
        self.series_cache = {}
        self.market_cap_cache = {}

        self.symbol_dict = {}
        self.google_dict = {}

        for dad in DataApiDict.objects.filter(api="YAHOO").all():
            self.symbol_dict[dad.platform_symbol] = dad.api_symbol

        for dad in DataApiDict.objects.filter(api="GOOGLE").all():
            self.google_dict[dad.platform_symbol] = dad.api_symbol

    def get_rate(self, currency, date):
        y, m, d = date.split("-")
        formatted_date = "{y}-{m}".format(**locals())

        rand = random.random()
        now = datetime.now()
        year = now.year
        month = now.month

        end = "{year}-{month}-01".format(**locals())

        url = "http://www.myfxbook.com/getHistoricalDataByDate.json?" \
              "&start=2008-02-01%2000:00&end={end}%2000:00&symbol={symbol}"\
              "&timeScale=43200&userTimeFormat=0&rand={rand}".format(rand=rand, symbol=currency, end=end)
        currency_cache = self.historical_currency_cache.get(currency, {})
        
        if not currency_cache:
            # get data from the net
            try:
                with urllib.request.urlopen(url) as response:
                    html_file = json.loads(response.read().decode("utf-8"))["content"]["historyData"]
                    soup = BeautifulSoup(html_file, "html.parser")
                    rows = soup.find_all("tr")
                    for row in rows:
                        columns = row.find_all("td")
                        if not columns:
                            continue
                        try:
                            _date, price = datetime.strptime(columns[0].text, "%b %d, %Y %H:%M"), float(columns[4].text)
                        except (IndexError, ValueError):
                            continue
                        currency_cache[_date.strftime("%Y-%m")] = price
            except urllib.request.HTTPError as e:
                raise Exception("{0} : {1}".format(e.msg, url))

            self.historical_currency_cache[currency] = currency_cache

        rate = currency_cache.get(formatted_date, 1)
        return rate

    def to_aud_historical(self, price, date, currency):
        if currency == "AUD":
            return price

        if currency == "USD":
            return (1/self.get_rate('AUDUSD', date)) * price;
        if currency == "GBP":
            return self.get_rate('GBPAUD', date) * price

    def get_all_prices(self, ticker_symbol, period="m", currency="AUD"):
        if ticker_symbol in self.series_cache:
            return self.series_cache[ticker_symbol]

        if ticker_symbol in ["UBJ", "UBE", "UBP", "UBJ", "UBW", "UBA"]:
            price_data = TradingRoomApi().get_all_prices(ticker_symbol,
                                                         period="m",
                                                         currency="AUD")

            self.series_cache[ticker_symbol] = Series(price_data,
                                                      index=self.dates,
                                                      name=ticker_symbol)
            return self.series_cache[ticker_symbol]

        if period == "m":
            self.dates = pd.date_range('2010-01-01', '{0}-{1}-01'
                                       .format(self.today_year, self.today_month+1), freq='M')
        elif period == "d":
            self.dates = pd.date_range('2010-01-01', '{0}-{1}-{2}'
                                       .format(self.today_year, self.today_month+1,
                                               self.today_day), freq='D')

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
                    close = self.to_aud_historical(float(cells[4]), date, currency)
                    price_data[pd.to_datetime(date)] = close
        except urllib.request.HTTPError as e:
            raise Exception("{0} : {1}".format(e.msg, url))

        if period == "m":
            for date, price in price_data.items():
                mp, is_new = MonthlyPrices.objects.get_or_create(date=date, symbol=db_symbol)
                mp.price = price
                mp.save()
        self.series_cache[ticker_symbol] = Series(price_data, index=self.dates, name=db_symbol)
        return self.series_cache[ticker_symbol]

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
        """
        :param ticker: The name of the symbol.
        :return: Market capitalisation in AUD
        """
        if ticker.symbol in self.market_cap_cache:
            return self.market_cap_cache[ticker.symbol]
        ticker_symbol = self.symbol_dict.get(ticker.symbol, ticker.symbol)
        url = "http://finance.yahoo.com/q?s={0}".format(ticker_symbol)
        with urllib.request.urlopen(url) as response:
            soup = BeautifulSoup(response, "html.parser")
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
        self.market_cap_cache[ticker.symbol] = value
        return self.market_cap_cache[ticker.symbol]


class TradingRoomApi:

     def get_all_prices(self, ticker_symbol, period="m", currency="AUD"):

        url = "http://www.tradingroom.com.au/apps/qt/csv/pricehistory.ac?section=yearly_price_download&code={symbol}" \
              "&ignore=.csv".format(symbol=ticker_symbol)

        price_data = {}
        dates = []
        closes = []
        min_date = None
        max_date = None
        try:
            with urllib.request.urlopen(url) as response:
                csv_file = response.read().decode("utf-8").splitlines()
                line_counter = 0
                for line in csv_file:
                    if line_counter == 0:
                        line_counter += 1
                        continue
                    cells = line.split(",")
                    close = float(cells[4])
                    if int(close) == 0:
                        continue
                    date = time.mktime(datetime.strptime(cells[0], "%d-%b-%Y").timetuple())
                    if min_date is None:
                        min_date = date
                    if max_date is None:
                        max_date = date
                    if date > max_date:
                        max_date = date
                    if date < min_date:
                        min_date = date
                    dates.append(date)
                    closes.append(close)
        except urllib.request.HTTPError as e:
            raise Exception("{0} : {1}".format(e.msg, url))
        y_interp = scipy.interpolate.interp1d(np.array(dates), np.array(closes), kind='cubic')

        min_datetime = datetime.fromtimestamp(min_date)
        next_date = min_datetime
        while True:
            # get current_date
            last_day = calendar.monthrange(next_date.year, next_date.month)[1]
            last_day_date_str = "{year}-{month}-{day}".format(year=next_date.year,
                                                              month=next_date.month,
                                                              day=last_day)
            last_day_date = datetime.strptime(last_day_date_str, "%Y-%m-%d")
            last_day_time = time.mktime(last_day_date.timetuple())
            if last_day_time < max_date:
                price_data[pd.to_datetime(last_day_date_str)] = y_interp(last_day_time)
            else:
                break

            next_date = next_date + relativedelta(months=1)

        for date, price in price_data.items():
            mp, is_new = MonthlyPrices.objects.get_or_create(date=date, symbol=ticker_symbol)
            mp.price = price
            mp.save()
        return price_data
'''


