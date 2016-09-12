from datetime import timedelta

from abc import ABC, abstractmethod


class DataProviderAbstract(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def set_cache(self, *args):
        pass

    def get_start_date(self):
        return self.get_current_date() - timedelta(days=365*5)

    @abstractmethod
    def get_instruments(self):
        pass

    @abstractmethod
    def move_date_forward(self):
        pass

    @abstractmethod
    def get_current_date(self):
        pass

    def get_features(self, ticker):
        pass

    @abstractmethod
    def get_asset_class_to_portfolio_set(self):
        pass

    @abstractmethod
    def get_portfolio_sets_ids(self):
        pass

    @abstractmethod
    def get_asset_feature_values_ids(self):
        pass

    @abstractmethod
    def get_tickers(self):
        pass

    @abstractmethod
    def get_ticker(self, id):
        pass

    @abstractmethod
    def get_market_weight(self, content_type_id, content_object_id):
        pass

    @abstractmethod
    def get_masks(self, instruments, fund_mask_name, portfolio_set_mask_prefix):
        pass

    @abstractmethod
    def get_goals(self):
        pass

    @abstractmethod
    def get_markowitz_scale(self):
        pass

    @abstractmethod
    def set_markowitz_scale(self, date, min, max, a, b ,c):
        pass
