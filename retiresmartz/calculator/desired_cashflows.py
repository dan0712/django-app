from __future__ import unicode_literals

import datetime

from dateutil.relativedelta import relativedelta

from .base import DesiredCashFlow


class RetirementDesiredCashFlow(DesiredCashFlow):
    def __init__(self, expected_income: float,
                 retirement_date: datetime.date,
                 retirement_years: float):
        self.expected_income = expected_income
        self.retirement_date = retirement_date
        self.last_date = retirement_date + \
                         relativedelta(years=retirement_years)
        self.retirement_years = retirement_years

        self._cur_date = None

    def __iter__(self):
        self.reset()
        return self

    def next(self) -> (datetime.date, float):
        if self._cur_date <= self.last_date:
            inflation = self.inflation_on(self._cur_date)
            payment = self.expected_income * (1 + inflation)
            cur_date = self._cur_date
            self._cur_date += relativedelta(months=1)
            return cur_date, payment
        raise StopIteration()

    def reset(self):
        self._cur_date = self.retirement_date
