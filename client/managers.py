from __future__ import unicode_literals

from django.db import models
from django.db.models import Q

from main.models import GoalMetric


class ClientQuerySet(models.query.QuerySet):
    def filter_by_user(self, user):
        if user.is_advisor:
            return self.filter_by_advisor(user.advisor)
        elif user.is_client:
            return self.filter(pk=user.client.pk)
        else:
            return self.none()

    def filter_by_firm(self, firm):
        """
        For now we only allow the firms of the client's main advisor
        """
        return self.filter(advisor__firm=firm)

    def filter_by_advisor(self, advisor):
        """
        For any client, the list of authorised advisors is as follows:
        - Advisor of the client
        - Secondary advisor of the client

        This method filters out any ClientAccounts where the given advisor is not one of the authorised advisors.
        """
        return self.filter(
            Q(advisor=advisor) |
            Q(secondary_advisors__pk=advisor.pk)
        )

    def filter_by_risk_level(self, risk_levels=None):
        """
        High Experimental
        """
        if risk_levels is None:
            return self

        if isinstance(risk_levels, int):
            risk_levels = [risk_levels, ]
        else:
            risk_levels = [int(r) for r in risk_levels]

        q = Q()
        for level in risk_levels:
            risk_min, risk_max = GoalMetric.risk_level_range(level)
            q |= Q(primary_accounts__all_goals__approved_settings__metric_group__metrics__configured_val__gte=risk_min,
                   primary_accounts__all_goals__approved_settings__metric_group__metrics__configured_val__lt=risk_max)
        qs = self.filter(q, primary_accounts__all_goals__approved_settings__metric_group__metrics__type=GoalMetric.METRIC_TYPE_RISK_SCORE)

        return qs


class ClientAccountQuerySet(models.query.QuerySet):
    def filter_by_firm(self, firm):
        """
        For now we only allow firms of the account's primary owner's primary advisor
        """
        return self.filter(primary_owner__advisor__firm=firm)

    def filter_by_advisor(self, advisor):
        """
        For any client account, the list of authorised advisors is as follows:
        - Primary advisor of the primary account owner
        - One of the secondary advisors of the primary account owner
        - Primary advisor of one of the account signatories
        - One of the secondary advisors of the account signatories
        - Primary advisor for the account group
        - One of the secondary advisors for the account group

        This method filters out any ClientAccounts where the given advisor is not one of the authorised advisors.
        """
        return self.filter(
            Q(primary_owner__advisor=advisor) |
            Q(primary_owner__secondary_advisors__pk=advisor.pk) |
            Q(signatories__advisor=advisor) |
            Q(signatories__secondary_advisors__pk=advisor.pk) |
            Q(account_group__advisor=advisor) |
            Q(account_group__secondary_advisors__pk=advisor.pk)
        )

    def filter_by_client(self, client):
        """
        For any client account, the list of authorised clients is as follows:
        - primary account owner
        - one of the account signatories

        This method filters out any ClientAccounts where the given client is not one of the authorised clients.
        """
        return self.filter(
            Q(primary_owner=client) |
            Q(signatories__pk=client.pk)
        )

    def filter_by_risk_level(self, risk_levels=None):
        """
        High Experimental
        """
        if risk_levels is None:
            return self

        if isinstance(risk_levels, int):
            risk_levels = [risk_levels, ]
        else:
            risk_levels = [int(r) for r in risk_levels]

        q = Q()
        for level in risk_levels:
            risk_min, risk_max = GoalMetric.risk_level_range(level)
            q |= Q(all_goals__approved_settings__metric_group__metrics__configured_val__gte=risk_min,
                   all_goals__approved_settings__metric_group__metrics__configured_val__lt=risk_max)
        qs = self.filter(q, all_goals__approved_settings__metric_group__metrics__type=GoalMetric.METRIC_TYPE_RISK_SCORE)

        return qs
