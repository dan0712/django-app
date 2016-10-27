from __future__ import unicode_literals

import datetime

from django.utils.timezone import now

from retiresmartz.models import InflationForecast


class FinancialResource:

    def reset(self):
        raise NotImplementedError()

    def inflation_on(self, asof: datetime.date):
        """
        Returns the inflation between
        :param asof:
        :return:
        """


# noinspection PyAbstractClass
class DesiredCashFlow(FinancialResource):
    def __iter__(self):
        return self

    def __next__(self) -> (datetime.date, float):
        return self.next()

    def next(self) -> (datetime.date, float):
        raise NotImplementedError()
