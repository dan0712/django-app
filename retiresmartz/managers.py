from __future__ import unicode_literals

import datetime
import logging
from typing import Iterable

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
    def on_date(self, begin_date: datetime.date,
                end_date: datetime.date) -> float:
        begin_date = begin_date.replace(day=1)
        end_date = end_date.replace(day=1)
        if begin_date >= end_date:
            raise ValueError('End date must be after begin date.')

        try:
            first_month = self.filter(date__gte=begin_date)[0]
            last_month = self.filter(date__lt=end_date).order_by('-date')[0]
        except IndexError:
            return 0.

        return (last_month.value / first_month.value) - 1
