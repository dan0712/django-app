from abc import ABC, abstractmethod


class IBroker(ABC):
    def __init__(self):
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






