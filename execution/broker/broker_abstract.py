from abc import ABC, abstractmethod


class BrokerAbstract(ABC):
    def __init__(self):
        pass

    def _register(self, method, *subscription):
        pass

    def connect(self):
        return True

    def disconnect(self):
        pass

    def request_account_summary(self):
        pass






