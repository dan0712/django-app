from __future__ import unicode_literals

import datetime
from abc import abstractmethod, ABCMeta

from common.utils import months_between
from main.models import Inflation
from .base import FinancialResource


class CashFlow(FinancialResource):
    __metaclass__ = ABCMeta

    # these dates to set the boundaries when to produce money
    start_date = None
    end_date = None
    last_date = None

    def on(self, dt: datetime.date) -> float:
        """
        Returns non-discretionary cash flow for that
        month. Must be called with monotonically increasing months between
        calls to reset(). The CashFlow is assumed applied independent of
        whether on() is called at any moment.
        """
        if self.last_date > dt:
            raise ValueError("Order of dates must be monotonically increasing between resets.")

        self.last_date = dt

        return self._for_date(dt) if self.start_date <= dt <= self.end_date else 0

    @abstractmethod
    def _for_date(self, date: datetime.date) -> float:
        raise NotImplementedError()

    def reset(self):
        self.last_date = self.start_date


class ReverseMortgage(CashFlow):
    def __init__(self,
                 home_value: float,
                 value_date: datetime.date,
                 start_date: datetime.date,
                 end_date: datetime.date):
        """
        Initialises a reverse mortgage calculator
        :param home_value:
        :param value_date:
        :param start_date:
        :param end_date:
        """
        self.start_date = start_date
        self.end_date = end_date
        self.last_date = start_date
        home_value_at_retirement = home_value * (1 + Inflation.between(value_date, start_date))
        self.monthly_payment = home_value_at_retirement * 0.9 / months_between(start_date, end_date)

    def _for_date(self, date: datetime.date) -> float:
        return self.monthly_payment


class SocialSecurity(CashFlow):
    def __init__(self, birthday: datetime.date,
                 retirement_date: datetime.date):
        self.birthday = birthday
        self.retirement_date = retirement_date

    def _for_date(self, date: datetime.date) -> float:
        return 0.


class AccountContribution(CashFlow):
    def __init__(self, current_income: float, percent: float,
                 end_date: datetime.date):
        assert 0. < percent < 1., 'Wrong percent value'
        self.current_income = current_income
        self.percent = percent
        self.end_date = end_date

    def on(self, date: datetime.date) -> float:
        if (self.start_date is not None and self.start_date < date) or \
                (self.end_date is not None and self.end_date > date):
            return 0
        return self.current_income * self.percent * \
               (1 + self.inflation_on(date))

    def reset(self):
        pass


class JobIncome(CashFlow):
    def __init__(self, income: float, end_date: datetime.date):
        self.income = income
        self.end_date = end_date

    def on(self, date: datetime.date) -> float:
        if date > self.end_date:
            return 0
        return self.income * (1 + self.inflation_on(date))

    def reset(self):
        pass
