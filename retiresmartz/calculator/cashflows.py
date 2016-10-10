from __future__ import unicode_literals

import datetime

from dateutil.relativedelta import relativedelta

from .base import FinancialResource


# noinspection PyAbstractClass
class CashFlow(FinancialResource):
    # these dates to set the boundaries when to produce money
    start_date = None
    end_date = None

    def on(self, date: datetime.date) -> float:
        """
        Returns non-discretionary cash flow for that
        month. Must be called with monotonically increasing months between
        calls to reset(). The CashFlow is assumed applied independent of
        whether on() is called at any moment.
        """
        raise NotImplementedError()


class ReverseMortgage(CashFlow):
    def __init__(self, home_value: float,
                 retirement_date: datetime.date,
                 retirement_years: int):
        self.retirement_date = retirement_date
        self.retirement_years = retirement_years
        self.last_date = retirement_date + \
                         relativedelta(years=retirement_years)
        self.future_home_value = home_value * (
            1 + (self.inflation_on(self.last_date) / 12)
        )

        self.monthly_payment = (self.future_home_value * .9 /
                                self.retirement_years) / 12

    def on(self, date: datetime.date) -> float:
        if self.retirement_date <= date <= self.last_date:
            return self.monthly_payment
        return 0.

    def reset(self):
        pass


class SocialSecurity(CashFlow):
    def __init__(self, birthday: datetime.date,
                 retirement_date: datetime.date):
        self.birthday = birthday
        self.retirement_date = retirement_date

    def on(self, date: datetime.date) -> float:
        return 0.

    def reset(self):
        pass


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
