from __future__ import unicode_literals

import datetime
from abc import ABCMeta, abstractmethod

from dateutil.relativedelta import relativedelta

from main.models import Inflation
from retiresmartz.constants import IRS_LIFE_EXPECTANCY
from .base import FinancialResource
from .cashflows import CashFlow


class Asset(FinancialResource):
    __metaclass__ = ABCMeta

    @abstractmethod
    def withdraw(self, date: datetime.date, amount: float) -> float:
        """
        Try to withdraw the given amount from the account on the given date. May return less than requested.
        This method and balance() must be called with monotonically increasing months between calls to reset()
        :param date: The date of the withdrawal
        :param amount: The desired amount of the withdrawal
        :return Some value <= amount which is the amount that is allowed/available to be withdrawn at this time.
        """
        raise NotImplementedError()

    @abstractmethod
    def balance(self, date: datetime.date) -> float:
        """
        The balance of the account at the given date. Dependent of previous withdrawals made and date called.
        This method and withdraw() must be called with monotonically increasing months between calls to reset()
        """
        raise NotImplementedError()


class TaxPaidAccount(Asset):
    def __init__(self,
                 name: str,
                 today: datetime.date,
                 opening_balance: float,
                 growth: float,
                 retirement_date: datetime.date,
                 end_date: datetime.date,
                 contributions: float):
        """
        An account that has no tax applied
        :param name: Account name
        :param today: The day the calculations are run.
        :param opening_balance: The balance of the asset today
        :param growth: Expected annual growth of the asset over inflation 0.05 = 5%
        :param retirement_date: Withdrawals are only possible after this date. Contributions stop on this date.
        :param end_date: Date the account should stop paying money.
        :param contributions: Monthly contributions into the account at today's dollars
        """
        self.name = name
        self._today = today
        self._opening_balance = opening_balance
        self._growth_factor = (1 + growth) ** (1 / 12)
        self._retirement_date = retirement_date
        self._end_date = end_date
        self._contributions = contributions
        self._current_balance = opening_balance
        self._current_date = today

    def _update_balance(self, date: datetime.date):
        tdt = self._current_date + relativedelta(months=1)
        while tdt <= date:
            # Grow the asset for the month
            self._current_balance *= (self._growth_factor + Inflation.between(self._current_date, tdt))
            # Add the contributions at the end of the month.
            if tdt <= self._retirement_date:
                self._current_balance += self._contributions * (1 + Inflation.between(self._today, tdt))
            self._current_date = tdt
            tdt = self._current_date + relativedelta(months=1)

    def balance(self, date: datetime.date) -> float:
        # date must be >= _current_date
        if date < self._current_date:
            raise ValueError('Only ascending values allowed.')

        self._update_balance(date)
        return self._current_balance

    def withdraw(self, date: datetime.date, amount: float) -> float:
        # date must be >= _current_date
        if date < self._current_date:
            raise ValueError('Only ascending values allowed.')

        if date < self._retirement_date or date > self._end_date:
            return 0

        self._update_balance(date)

        # withdraw as much of amount as possible
        balance = self._current_balance
        if balance < amount:
            self._current_balance = 0
            return balance
        self._current_balance = balance - amount
        return amount

    def reset(self):
        self._current_date = self._today
        self._current_balance = self._opening_balance


class TaxDeferredAccount(TaxPaidAccount, CashFlow):
    """
    A Tax Deferred Account acts like a CashFlow as it has a required minimum distribution aspect.
    Withdrawals are taxed.
    """

    def __init__(self, dob: datetime.date, tax_rate: float, *args, **kwargs):
        self._dob = dob
        self._tax_multiplier = 1 - tax_rate
        super().__init__(*args, **kwargs)

    def withdraw(self, date: datetime.date, amount: float) -> float:
        avail_amount = super().withdraw(date, amount / self._tax_multiplier)
        return avail_amount * self._tax_multiplier

    def _for_date(self, dt: datetime.date):
        age = relativedelta(dt, self._dob).years
        # We only want to draw the balance down by the required amount, not the required amount plus tax, so we multiply
        # by the tax multiplier so the actual amount withdrawn before tax is the required proportion.
        amount = self.balance(dt) / IRS_LIFE_EXPECTANCY[age] * self._tax_multiplier
        return self.withdraw(dt, amount)
