from __future__ import unicode_literals

import datetime
from abc import abstractmethod, ABCMeta

from dateutil.relativedelta import relativedelta

from common.utils import months_between
from main.models import Inflation
from .base import FinancialResource


class CashFlow(FinancialResource):
    __metaclass__ = ABCMeta

    # these dates to set the boundaries when to call _for_date(). If unset, they will always call it.
    start_date = None
    end_date = None
    current_date = None

    def on(self, dt: datetime.date) -> float:
        """
        Returns non-discretionary cash flow for that
        month. Must be called with monotonically increasing months between
        calls to reset(). The CashFlow is assumed applied independent of
        whether on() is called at any moment.
        """
        if self.current_date and self.current_date > dt:
            raise ValueError("Order of dates must be monotonically increasing between resets.")

        # Do not give the income twice for the same day
        if self.current_date == dt:
            return 0

        self.current_date = dt

        if (self.start_date and self.start_date > dt) or (self.end_date and dt > self.end_date):
            return 0

        return self._for_date(dt)

    @abstractmethod
    def _for_date(self, date: datetime.date) -> float:
        raise NotImplementedError()

    def reset(self):
        self.current_date = None


class ReverseMortgage(CashFlow):
    def __init__(self,
                 home_value: float,
                 value_date: datetime.date,
                 start_date: datetime.date,
                 end_date: datetime.date):
        """
        Initialises a reverse mortgage calculator
        :param home_value:
        :param value_date: The date the home was valued. Must be <= start_date
        :param start_date: The day the reverse mortgage should start paying (Usually the retirement date)
        :param end_date: The day the reverse mortgage should end (Usually the death of the last family member)
        """
        self.start_date = start_date
        self.end_date = end_date
        home_value_at_start_date = home_value * (1 + Inflation.between(value_date, start_date))
        self.monthly_payment = home_value_at_start_date * 0.9 / months_between(start_date, end_date)

    def _for_date(self, date: datetime.date) -> float:
        return self.monthly_payment


class InflatedCashFlow(CashFlow):
    def __init__(self,
                 amount: float,
                 today: datetime.date,
                 start_date: datetime.date,
                 end_date: datetime.date):
        """
        :param amount: Amount per cash flow event
        :param today: Day to begin inflation of the amount
        :param start_date: Date to start the cash flow.
        :param end_date: Date the cash flow should stop
        """
        self._today = today
        self._amount = amount
        self.start_date = start_date
        self.end_date = end_date

    def _for_date(self, date: datetime.date) -> float:
        return self._amount * (1 + Inflation.between(self._today, date))


class EmploymentIncome(CashFlow):
    def __init__(self, income: float, growth: float, today: datetime.date, end_date: datetime.date):
        """
        Initialiser
        :param income: The monthly income as of 'today'
        :param today: The today date
        :param end_date: The time the income will stop
        :param growth: Expected annual income growth above CPI. 0.01 = 1%
        """
        self._growth_factor = (1 + growth) ** (1/12)
        self.start_date = today
        self._last_date = today
        self.end_date = end_date
        self._income = income
        self._current_income = income

    def _for_date(self, date: datetime.date) -> float:
        tdt = self._last_date + relativedelta(months=1)
        while tdt <= date:
            # Grow the income for the month
            self._current_income *= (self._growth_factor + Inflation.between(self._last_date, tdt))
            self._last_date = tdt
            tdt = self._last_date + relativedelta(months=1)
        return self._current_income

    def reset(self):
        super().reset()
        self._last_date = self.start_date
        self._current_income = self._income
