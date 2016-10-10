from __future__ import unicode_literals

import datetime

import scipy.stats as st
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

from .base import FinancialResource
from .cashflows import AccountContribution, CashFlow


# noinspection PyAbstractClass
class Asset(FinancialResource):
    # before this date no money can be withdrawn
    available_after = None

    name = None

    def withdraw(self, date: datetime.date, amount: float) -> float:
        """
        Try to withdraw the given amount
        on the given year and month. May return less than requested. Must be
        called with monotonically increasing months between calls to reset()
        """
        raise NotImplementedError()

    def balance(self, date: datetime.date) -> float:
        """
        The balance at that time. Dependent of
        previous withdrawals made and date called.
        """
        raise NotImplementedError()


class TaxPaidAccount(Asset):
    def __init__(self, name: str, balance: float,
                 retirement_date: datetime.date, life_exp: int):
        self.name = name
        self.retirement_date = retirement_date
        self.life_exp = life_exp
        self.end_date = retirement_date + relativedelta(years=life_exp)
        self.start_balance = balance

        self._contributions = set()
        self._current_date = None
        self._current_balance = None
        self._balances = {}

    def rer_forecast(self, balance: float,
                     end_date: datetime.date,
                     begin_date: datetime.date = None,
                     er=1.0, stdev=0.0, confidence=0.5) -> float:
        """
        Real Expected Return forecast for the period from between two dates
        from Growth Tables
        """
        current_time = now()
        if begin_date is None:
            begin_date = current_time.date()
        cf_events = [(begin_date, balance)]
        cur_date = begin_date + relativedelta(months=1)
        if self._contributions:
            while cur_date <= end_date:
                for c in self._contributions:  # type: AccountContribution
                    cf_events.append((cur_date, c.on(cur_date)))
                cur_date += relativedelta(months=1)

        z_mult = -st.norm.ppf(confidence)
        z_stdev = z_mult * stdev
        predicted = 0.
        for dt, val in cf_events:
            tdelta = dt - begin_date
            y_delta = (tdelta.days + tdelta.seconds / 86400.0) / 365.2425
            predicted += val * (er ** y_delta + z_stdev * (y_delta ** 0.5))
        return predicted

    @property
    def contributions(self):
        return self._contributions

    def add_contributions(self, *values: [CashFlow]):
        self._contributions |= set(values)

    def _check_date(self, date: datetime.date):
        if not (self.retirement_date <= date <= self.end_date):
            raise ValueError('Date out of boundaries.')

    def _balance(self, balance: float, date: datetime.date,
                 begin_date: datetime.date = None) -> float:
        rer_forecast = self.rer_forecast(balance, date, begin_date)
        return rer_forecast * (1 + self.inflation_on(date))

    def balance(self, date: datetime.date) -> float:
        return self._balance(self.start_balance, date)

    def withdraw(self, date: datetime.date, amount: float) -> float:
        self._check_date(date)

        try:
            if date < self.available_after:
                return 0
        except TypeError:  # available_after not set
            pass

        try:
            # date must be > _current_date
            if date <= self._current_date:
                raise ValueError('Only ascending values allowed.')
        except TypeError:  # first iteration, current date is not yet set
            pass

        # calculate balance on date
        if self._current_balance is not None and self._current_balance == 0:
            return 0
        balance = self._balance(self._current_balance or self.start_balance,
                                date, self._current_date)
        self._current_date = date

        # withdraw as much as amount if possible
        if balance < amount:
            self._current_balance = 0
            return balance
        self._current_balance = balance - amount
        return amount

    def reset(self, date: datetime.date = None):
        if not date:
            date = self.retirement_date
        self._check_date(date)
        self._current_date = None
        self._current_balance = None


class TaxDeferredAccount(TaxPaidAccount):
    def apply_taxes(self, date: datetime.date, amount: float):
        if amount > 0:
            pass  # calculate and subtract taxes
        return amount

    def withdraw(self, date: datetime.date, amount: float) -> float:
        avail_amount = super(TaxDeferredAccount, self).withdraw(date, amount)
        return self.apply_taxes(date, avail_amount)
