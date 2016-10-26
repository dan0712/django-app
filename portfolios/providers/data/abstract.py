from abc import ABC, abstractmethod


class DataProviderAbstract(ABC):
    @abstractmethod
    def get_instrument_daily_prices(self, ticker):
        raise NotImplementedError()

    @abstractmethod
    def get_instrument_cache(self):
        raise NotImplementedError()

    @abstractmethod
    def set_instrument_cache(self, data):
        raise NotImplementedError()

    @abstractmethod
    def get_current_date(self):
        raise NotImplementedError()

    def get_features(self, ticker):
        raise NotImplementedError()

    @abstractmethod
    def get_asset_class_to_portfolio_set(self):
        raise NotImplementedError()

    @abstractmethod
    def get_portfolio_sets_ids(self):
        raise NotImplementedError()

    @abstractmethod
    def get_asset_feature_values_ids(self):
        raise NotImplementedError()

    @abstractmethod
    def get_tickers(self):
        raise NotImplementedError()

    @abstractmethod
    def get_ticker(self, tid):
        raise NotImplementedError()

    @abstractmethod
    def get_market_weight(self, content_type_id, content_object_id):
        raise NotImplementedError()

    @abstractmethod
    def get_goals(self):
        raise NotImplementedError()

    @abstractmethod
    def get_markowitz_scale(self):
        raise NotImplementedError()

    @abstractmethod
    def set_markowitz_scale(self, date, mn, mx, a, b, c):
        raise NotImplementedError()

    @abstractmethod
    def get_fund_price_latest(self, ticker):
        raise NotImplementedError()

    @abstractmethod
    def get_investment_cycles(self):
        """
        Returns the query set containing the investment cycle observations ordered by ascending date
        up until the self.get_current_date().
        """
        raise NotImplementedError()

    @abstractmethod
    def get_last_cycle_start(self):
        """
        Get the beginning of the last complete investment cycle in our history.
        :return: The date of the first day of the last complete investment cycle.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_investment_cycle_predictions(self):
        """
        Returns the query set containing the investment cycle predictions ordered by ascending date
        up until the self.get_current_date().
        """
        raise NotImplementedError()

    @abstractmethod
    def get_cycle_obs(self, begin_date):
        """
        Returns a pandas timeseries dataframe with the cycle id as the value.
        :param begin_date: The earliest date you want the series from.
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def get_probs_df(self, begin_date):
        """
        return dataframe suitable for function get_normalized_probabilities of InvestmentClock
        :param begin_date: The earliest date you want the probabilities from
        :return: Dataframe
        """
        raise NotImplementedError()
