import pandas as pd
import pandas.io.data as web

from main.management.commands.rebalance import rebalance
from portfolios.calculation import build_instruments, \
    calculate_portfolio, calculate_portfolios
from portfolios.providers.data.backtester import DataProviderBacktester
from portfolios.providers.dummy_models import GoalFactory, PositionMock
from portfolios.providers.execution.backtester import ExecutionProviderBacktester


class GetETFTickers(object):
    def __init__(self, filePath):
        self.__filePath = filePath
        self.__data = None

    def loadCsv(self):
        self.__data = pd.read_csv(self.__filePath)

    def filterETFs(self):
        self.__data = self.__data.ix[self.__data['Industry'] == 'Exchange Traded Fund']
        self.__data = self.__data.ix[self.__data['Country'] == 'USA']
        self.__data = self.__data.sort('Volume', ascending=False)
        self.__data = self.__data.head(n=300)

    def returnData(self):
        return self.__data['Ticker'].tolist()


class DownloadDataYahoo(object):
    def __init__(self, start, end, tickerList):
        self.__tickerList = tickerList
        self.__start = start
        self.__end = end
        self.__data = None

    def download(self):
        self.__data = web.DataReader(self.__tickerList, 'yahoo', self.__start, self.__end)

    def returnData(self):
        return self.__data


class Backtester(object):
    def execute_order(self, settings, order, data_provider, execution_provider):
        for request in order[0].execution_requests:
            in_portfolio = False
            for position in settings.positions:
                if position.ticker.symbol == request.asset.symbol:
                    in_portfolio = True
                    ticker = data_provider.get_ticker(position.ticker.symbol)
                    share_value = ticker.daily_prices.last() * request.volume
                    settings.current_balance -= share_value
                    settings.cash_balance -= share_value
                    position.share += request.volume

            if not in_portfolio:
                ticker = data_provider.get_ticker(request.asset.symbol)
                share_value = ticker.daily_prices.last() * request.volume
                settings.current_balance -= share_value
                settings.cash_balance -= share_value
                position = PositionMock(ticker=ticker, share=request.volume)
                position.data_provider = data_provider
                settings.positions.append(position)
            execution_provider.order_executed(execution_request=request,
                                              price=ticker.daily_prices.last(),
                                              time=data_provider.get_current_date())
            execution_provider.attribute_sell(execution_request=request, goal=settings)
        execution_provider.cancel_pending_orders()
        execution_provider.cash_left(cash=settings.cash_balance, time=data_provider.get_current_date())

    def calculate_performance(self, execution_provider):
        return execution_provider.calculate_portfolio_returns()


class TestSetup(object):
    def __init__(self):
        self._covars = self._samples = self._instruments = self._masks = None
        self.data_provider = DataProviderBacktester(sliding_window_length=250*5)
        self.execution_provider = ExecutionProviderBacktester()
        self.goal = GoalFactory.create_goal(self.data_provider)

    def instruments_setup(self):
        self._covars, self._samples, self._instruments, self._masks = build_instruments(self.data_provider)


if __name__ == "__main__":
    '''
    tickers = GetETFTickers('finviz.csv')
    tickers.loadCsv()
    tickers.filterETFs()
    etfTickers = tickers.returnData()
    yahoo = DownloadDataYahoo(datetime.datetime(2005,1,1), datetime.datetime(2016,7,30), etfTickers)
    yahoo.download()
    dataClose = yahoo.returnData()['Close']
    dataClose[dataClose == 0] = np.nan
    dataClose.fillna('ffill')

    capitalization = yahoo.returnData()['Close'] * yahoo.returnData()['Volume']
    capitalization[capitalization==0]=np.nan
    capitalization.fillna('ffill')

    dataClose.to_csv('fundPrices.csv')
    capitalization.to_csv('capitalization.csv')
    '''

    setup = TestSetup()

    backtester = Backtester()
    requests = [setup.execution_provider.create_empty_market_order()]

    while setup.data_provider.move_date_forward():
        print("backtesting "+str(setup.data_provider.get_current_date()))

        build_instruments(setup.data_provider)

        '''

        # execute orders from yesterday
        backtester.place_order(settings=setup.goal,
                               order=requests,
                               data_provider=setup.data_provider,
                               execution_provider=setup.execution_provider)
        '''


        # calculate current portfolio stats
        portfolios_stats = calculate_portfolios(setting=setup.goal.active_settings,
                                                data_provider=setup.data_provider,
                                                execution_provider=setup.execution_provider)
        portfolio_stats = calculate_portfolio(settings=setup.goal.active_settings,
                                              data_provider=setup.data_provider,
                                              execution_provider=setup.execution_provider)

        # generate orders for tomorrow
        try:
            requests = rebalance(idata=setup.data_provider.get_instruments(),
                                 goal=setup.goal,
                                 data_provider=setup.data_provider,
                                 execution_provider=setup.execution_provider)
        except:
            print("reblance not succesful")
            requests = [setup.execution_provider.create_empty_market_order()]

        backtester.execute_order(settings=setup.goal,
                                 order=requests,
                                 data_provider=setup.data_provider,
                                 execution_provider=setup.execution_provider)

    performance = backtester.calculate_performance(execution_provider=setup.execution_provider)

    print('finished correctly')
