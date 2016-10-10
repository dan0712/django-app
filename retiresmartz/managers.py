from __future__ import unicode_literals

import datetime
import logging

from dateutil.relativedelta import relativedelta
from django.db.models import Max, Q, QuerySet
from django.utils.timezone import now

logger = logging.getLogger(__name__)


class RetirementPlanQuerySet(QuerySet):
    def filter_by_user(self, user):
        if user.is_advisor:
            return self.filter_by_advisor(user.advisor)
        elif user.is_client:
            return self.filter_by_client(user.client)
        else:
            return self.none()

    def filter_by_firm(self, firm):
        """
        For now we only allow the firms of the plan's owner's main advisor.
        """
        return self.filter(client__advisor__firm=firm)

    def filter_by_advisor(self, advisor):
        """
        This method filters out any Retirement Plans where the given advisor
        is not one of the authorised advisors.

        For any RetirementPlan, the list of authorised advisors is as follows:
        - Advisor of the client owning the plan
        - Secondary advisor of the client owning the plan
        - Advisor of the client owning the specified partner_plan
        - Secondary advisor of the client owning the specified partner_plan
        """
        return self.filter(
            Q(client__advisor=advisor) |
            Q(client__secondary_advisors__id=advisor.id) |
            Q(partner_plan__client__advisor=advisor) |
            Q(partner_plan__client__secondary_advisors__id=advisor.id)
        )

    def filter_by_client(self, client):
        """
        A client is allowed to see its own retirement plans, and any linked
        retirement plans via the partner_plan.
        :param client:
        :return: A modified queryset with access to only the authorised plans.
        """
        return self.filter(
            Q(client=client) |
            Q(partner_plan__client=client)
        )


class InflationForecastQuerySet(QuerySet):
    def load(self, data):
        """
        loads data from a iterable

        :param data: [(1/1/2016|2017, value), ...]
        """

        def create(y, r):
            d = datetime.date(y, 1, 1)
            v = []
            while d.year <= y:
                v.append(self.model(date=d, value=r))
                d += relativedelta(months=1)
            return v

        models = []
        last_year = None
        last_monthly_rate = None
        for input_date, value in data:  # type: str, float
            values = []
            monthly_rate = value / 12.
            try:
                year = float(input_date)
                if last_year is None:
                    last_year = year
                    last_monthly_rate = monthly_rate
                else:
                    if year - last_year > 1:  # cover 5 year forecast
                        for year in range(last_year + 1, year):
                            values.extend(create(year, last_monthly_rate))

                values = create(year, monthly_rate)
            except ValueError:  # it's date, not year
                date = datetime.date(input_date.split('/')[::-1])
                values.append(self.model(date=date, value=monthly_rate))
            models.extend(values)

    def on_date(self, end_date: datetime.date,
                begin_date: datetime.date = None,
                version: datetime.datetime = None) -> float:
        """
        :param end_date:
        :param begin_date: start date or use current date
        :param version: limit query to data created before or on a date
        :return:
        """
        if begin_date is None:
            begin_date = now().date()
        if begin_date > end_date:
            raise ValueError('Begin date must be greater than end date')

        # SELECT date, value, max(version) FROM t GROUP BY date
        kwargs = {
            'date__range': (begin_date, end_date),
        }
        if version is not None:
            kwargs['created_date__lte'] = version
        data = (self.filter(**kwargs).annotate(Max('created_date'))
                .values_list('value', flat=True))

        rate = float(sum(data))

        return rate
