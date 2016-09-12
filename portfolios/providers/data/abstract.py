from datetime import timedelta

from abc import ABC, abstractmethod


class DataProviderAbstract(ABC):
    @abstractmethod
    def set_cache(self, *args):
        raise NotImplementedError()

    def get_start_date(self):
        return self.get_current_date() - timedelta(days=365*5)

    @abstractmethod
    def get_instruments(self):
        raise NotImplementedError()

    @abstractmethod
    def move_date_forward(self):
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
    def get_ticker(self, id):
        raise NotImplementedError()

    @abstractmethod
    def get_market_weight(self, content_type_id, content_object_id):
        raise NotImplementedError()

    @abstractmethod
    def get_masks(self, instruments, fund_mask_name, portfolio_set_mask_prefix):
        raise NotImplementedError()

    @abstractmethod
    def get_goals(self):
        raise NotImplementedError()

    @abstractmethod
    def get_markowitz_scale(self):
        raise NotImplementedError()

    @abstractmethod
    def set_markowitz_scale(self, date, min, max, a, b ,c):
        raise NotImplementedError()
