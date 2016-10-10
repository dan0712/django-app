from __future__ import unicode_literals

import datetime

from retiresmartz.models import InflationForecast


class FinancialResource:
    def inflation_on(self, date: datetime.date):
        """
        Calculates inflation from now to date

        :param date:
        :return:
        """
        return InflationForecast.objects.on_date(date)

    def reset(self):
        raise NotImplementedError()


# noinspection PyAbstractClass
class DesiredCashFlow(FinancialResource):
    def __iter__(self):
        return self

    def __next__(self) -> (datetime.date, float):
        return self.next()

    def next(self) -> (datetime.date, float):
        raise NotImplementedError()
