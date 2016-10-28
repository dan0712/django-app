from __future__ import unicode_literals

import datetime

from dateutil.relativedelta import relativedelta

from main.models import Inflation
from retiresmartz.calculator.cashflows import CashFlow
from .base import DesiredCashFlow


class RetiresmartzDesiredCashFlow(DesiredCashFlow, CashFlow):
    """
    Generates a desired cash flow, and also provides employment cash flow
    """
    def __init__(self,
                 current_income: CashFlow,
                 retirement_income: float,
                 today: datetime.date,
                 retirement_date: datetime.date,
                 end_date: datetime.date):
        """
        Initialises the DesiredCashFlow Calculator
        :param current_income: Pre-retirement income cash-flow calculator
        :param retirement_income: desired monthly after tax income in retirement
        :param today: The as of date for the calculation
        :param retirement_date: The date to retire
        :param end_date: Likely death.
        """
        self._current_income = current_income
        self._retirement_income = retirement_income
        self._today = today
        self._retirement_date = retirement_date
        self._stop_date = end_date
        self._cur_payment = current_income

        self.start_date = today  # The date the cashflow becomes active
        self.end_date = retirement_date  # End date is when the CashFlow will stop
        self._current_date = today

    def __iter__(self):
        self._current_date = self._today
        return self

    def next(self) -> (datetime.date, float):
            if self._current_date <= self._retirement_date:
                self._cur_payment = self._current_income.on(self._current_date)
            else:
                self._cur_payment = self._retirement_income * (1 + Inflation.between(self._today, self._current_date))
            self._current_date += relativedelta(months=1)
            if self._current_date > self._stop_date:
                raise StopIteration()
            return self._current_date, self._cur_payment

    def _for_date(self, date: datetime.date):
        assert date == self._current_date
        return self._cur_payment
