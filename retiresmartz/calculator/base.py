from __future__ import unicode_literals

import datetime
from abc import ABCMeta, abstractmethod


class FinancialResource:
    __metaclass__ = ABCMeta

    @abstractmethod
    def reset(self):
        raise NotImplementedError()


class DesiredCashFlow(FinancialResource):
    __metaclass__ = ABCMeta

    def __iter__(self):
        return self

    def __next__(self) -> (datetime.date, float):
        return self.next()

    @abstractmethod
    def next(self) -> (datetime.date, float):
        raise NotImplementedError()
