from abc import ABC, abstractmethod


class IBroker(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def current_time(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def request_account_summary(self):
        pass

    @abstractmethod
    def request_market_depth(self, ticker):
        pass

    @abstractmethod
    def requesting_market_depth(self):
        pass

    @abstractmethod
    def make_order(self, ticker, quantity, limit_price):
        pass

    @abstractmethod
    def place_order(self, ib_id):
        pass

    @abstractmethod
    def place_orders(self):
        pass

    @abstractmethod
    def request_current_time(self):
        pass

    @staticmethod
    def is_advisor_account(account):
        if 'DF' in account:
            return True
        else:
            return False

