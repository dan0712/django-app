class Backtester(object):
    def __init__(self, fund_sel_algo, opt_algo, rebal_algo, risk_algo, view_algo):
        """
        :param fund_sel_algo:
            The algo that filters from the universe of funds to the funds available to our portfolio optimiser.
        :param opt_algo:
            The algo that takes the list of funds and data about them, and some settings and creates an actual
            investment portfolio.
        :param rebal_algo:
            Algo that takes a collection of current holdings for a portfolio, a settings object and the data about
            the instruments in the system and generates any required changes to the holdings as orders.
        :param risk_algo:
            Algo that takes the current instrument data and provides conversion form a risk_score to parameters used by
            the rebal and opt algos, as well as a measurement technique to measure the risk_score of the current
            portfolio holdings.
        :param view_algo:
            given current instrument data, generates a set of BL views.
        """
        pass

    def get_funds(self, dt):
        """
        Returns a pandas dataframe of all funds in the universe as at the given date.
        This return value is used as the input to the fund selection algorithm
        :return:
        """
        pass

    def get_data(self, dt):
        """
        Returns an InstrumentData object for the given date that can be used to run an optimisation or
        rebalance against.
        :param dt:
        :return:
        """
        pass

    def place_order(self, order):
        """
        Takes a placed market order and executes is appropriately, updating the internal statistics of the
        platform.
        :param order: A MarketOrderRequest
        :return: None
        """
        pass

    def run(self, start_date, end_date, settings):
        """
        :param start_date:
        :param end_date:
        :param settings:
        :return:
        """

        #  for each day, do stuff.