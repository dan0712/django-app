from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.db.models.query_utils import Q
from django.utils.timezone import now


class RetirementPlanQuerySet(models.query.QuerySet):
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
        This method filters out any Retirement Plans where the given advisor is not one of the authorised advisors.

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
        A client is allowed to see its own retirement plans, and any linked retirement plans via the partner_plan.
        :param client:
        :return: A modified queryset with access to only the authorised plans.
        """
        return self.filter(
            Q(client=client) |
            Q(partner_plan__client=client)
        )


class GoalQuerySet(models.query.QuerySet):
    def filter_by_firm(self, firm):
        """
        For now we only allow firms of the goal's account's primary owner's advisor
        """
        return self.filter(account__primary_owner__advisor__firm=firm)

    def filter_by_advisor(self, advisor):
        """
        For any Goal, the list of authorised advisors is as follows:
        - Primary advisor of the primary account owner for the goal's account.
        - One of the secondary advisors of the primary account owner for the goal's account.
        - Primary advisor of one of the account signatories for the goal's account.
        - One of the secondary advisors of the account signatories for the goal's account.
        - Primary advisor for the account group for the goal's account.
        - One of the secondary advisors for the account group for the goal's account.

        This method filters out any Goals where the given advisor is not one of the authorised advisors.
        """
        return self.filter(
            Q(account__primary_owner__advisor=advisor) |
            Q(account__primary_owner__secondary_advisors__pk=advisor.pk) |
            Q(account__signatories__advisor=advisor) |
            Q(account__signatories__secondary_advisors__pk=advisor.pk) |
            Q(account__account_group__advisor=advisor) |
            Q(account__account_group__secondary_advisors__pk=advisor.pk)
        )

    def filter_by_client(self, client):
        """
        For any Goal, the list of authorised clients is as follows:
        - primary account owner for the goal's account
        - one of the account signatories for the goal's account

        This method filters out any Goals where the given client is not one of the authorised clients.
        """
        return self.filter(
            Q(account__primary_owner=client) |
            Q(account__signatories__pk=client.pk)
        )

    def filter_by_client_age(self, age_min=0, age_max=1000):
        """
        Experimental
        """
        current_date = now().today()
        range_dates = map(lambda x: current_date - relativedelta(years=x),
                          [age_max, age_min]) # yes, max goes first

        qs = self.filter(account__primary_owner__date_of_birth__range=range_dates)
        return qs

    def filter_by_risk_level(self, risk_level=None):
        """
        Experimental
        """
        if risk_level is None:
            return self

        from .models import GoalMetric
        risk_min, risk_max = GoalMetric.risk_level_range(risk_level)

        qs = self.filter(
            selected_settings__metric_group__metrics__type=GoalMetric.METRIC_TYPE_RISK_SCORE,
            selected_settings__metric_group__metrics__configured_val__gte=risk_min,
            selected_settings__metric_group__metrics__configured_val__lt=risk_max
        )
        return qs


class PositionQuerySet(models.query.QuerySet):
    def filter_by_firm(self, firm):
        qs = self.filter(goal__account__account_group__advisor__firm=firm.pk)
        return qs

    def filter_by_advisor(self, advisor):
        # TODO: should we add here "secondary_advisors"?
        qs = self.filter(goal__account__account_group__advisor=advisor.pk)
        return qs

    def filter_by_client(self, client):
        qs = self.filter(goal__account__primary_owner=client.pk)
        return qs

    # OBSOLETED
    #def filter_by_risk_level(self, risk_level=None):
    #    """
    #    Experimental
    #    """
    #    if not risk_level:
    #        return self
    #
    #    from .models import GoalType
    #    risk_min, risk_max = GoalType.risk_level_range(risk_level)
    #
    #    qs = self.filter(
    #        goal__type__risk_sensitivity__gte=risk_min,
    #        goal__type__risk_sensitivity__lt=risk_max
    #    )
    #    return qs

    def filter_by_risk_level(self, risk_level=None):
        """
        Experimental
        """
        if risk_level is None:
            return self

        from .models import GoalMetric
        risk_min, risk_max = GoalMetric.risk_level_range(risk_level)

        qs = self.filter(
            goal__selected_settings__metric_group__metrics__type=GoalMetric.METRIC_TYPE_RISK_SCORE,
            goal__selected_settings__metric_group__metrics__configured_val__gte=risk_min,
            goal__selected_settings__metric_group__metrics__configured_val__lt=risk_max
        )
        return qs

    def annotate_value(self):
        """
        Experimental

        NB. queryset supposed to have .values('xxx') declaration
        """
        qs = self.annotate(value=Coalesce(Sum(F('share') * F('ticker__unit_price')),0))
        return qs

    def aggregate_value(self):
        """
        Experimental
        """
        qs = self.aggregate(value=Coalesce(Sum(F('share') * F('ticker__unit_price')), 0))
        return qs


class ExternalAssetQuerySet(models.query.QuerySet):
    def filter_by_user(self, user):
        if user.is_advisor:
            return self.filter_by_advisor(user.advisor)
        elif user.is_client:
            return self.filter_by_client(user.client)
        else:
            return self.none()

    def filter_by_firm(self, firm):
        """
        For now we only allow firms of the asset's owner's primary advisor
        """
        return self.filter(owner__advisor__firm=firm)

    def filter_by_advisor(self, advisor):
        """
        For any asset, the list of authorised advisors is as follows:
        - Primary advisor of the asset owner
        - One of the secondary advisors of the asset owner

        This method filters out any assets where the given advisor is not one of the authorised advisors.
        """
        return self.filter(
            Q(owner__advisor=advisor) |
            Q(owner__secondary_advisors__pk=advisor.pk)
        )

    def filter_by_client(self, client):
        """
        For any asset, the list of authorised clients is as follows:
        - asset owner

        This method filters out any assets where the given client is not one of the authorised clients.
        """
        return self.filter(owner=client)

