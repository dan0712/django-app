from dateutil.relativedelta import relativedelta
from django.db.models import F, QuerySet, Sum
from django.db.models.functions import Coalesce
from django.db.models.query_utils import Q
from django.utils.timezone import now
from django.db.models.loading import get_model
import logging

logger = logging.getLogger('main.managers')


class AccountTypeQuerySet(QuerySet):
    def filter_by_user(self, user):
        if user.is_advisor:
            return self.filter_by_advisor(user.advisor)
        elif user.is_client:
            return self.filter_by_client(user.client)
        else:
            return self.none()

    def filter_by_advisor(self, advisor):
        return self.filter(id__in=advisor.firm.account_types.all())

    def filter_by_client(self, client):
        return self.filter_by_advisor(client.advisor)


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


class GoalQuerySet(QuerySet):
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
        q = Q()
        q |= Q(account__primary_owner__advisor=advisor) | \
            Q(account__primary_owner__secondary_advisors__pk=advisor.pk) | \
            Q(account__signatories__advisor=advisor) | \
            Q(account__signatories__secondary_advisors__pk=advisor.pk)

        # ClientAccounts are not guaranteed to have account groups
        # filtering breaks here if no account group so we're ignoring these
        # for the moment
        # Q(account__account_group__advisor=advisor) |
        # Q(account__account_group__secondary_advisors__pk=advisor.pk)
        return self.filter(q)

    def filter_by_advisors(self, advisors):
        """
        Accepts list of multiple advisors and filters by them, together.
        """
        q = Q()
        for advisor in advisors:
            q |= Q(account__primary_owner__advisor=advisor) | \
                Q(account__primary_owner__secondary_advisors__pk=advisor.pk) | \
                Q(account__signatories__advisor=advisor) | \
                Q(account__signatories__secondary_advisors__pk=advisor.pk)
        return self.filter(q)

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

    def filter_by_clients(self, clients):
        """
        Accepts list of multiple advisors and filter by them, together.
        """
        q = Q()
        for client in clients:
            q |= Q(account__primary_owner=client) | \
                Q(account__signatories__pk=client.pk)
        return self.filter(q)

    def filter_by_client_age(self, age_min=0, age_max=1000):
        """
        Experimental
        """
        current_date = now().today()
        range_dates = map(lambda x: current_date - relativedelta(years=x),
                          [age_max, age_min]) # yes, max goes first

        qs = self.filter(account__primary_owner__date_of_birth__range=range_dates)
        return qs

    def filter_by_risk_level(self, risk_levels=None):
        """
        Experimental
        """
        if risk_levels is None:
            return self

        from .models import GoalMetric

        if isinstance(risk_levels, int):
            risk_levels = [risk_levels, ]
        else:
            risk_levels = [int(r) for r in risk_levels]

        q = Q()
        for level in risk_levels:
            risk_min, risk_max = GoalMetric.risk_level_range(level)
            q |= Q(selected_settings__metric_group__metrics__configured_val__gte=risk_min,
                   selected_settings__metric_group__metrics__configured_val__lt=risk_max)
        qs = self.filter(q, selected_settings__metric_group__metrics__type=GoalMetric.METRIC_TYPE_RISK_SCORE)

        return qs

    def filter_by_worth(self, worth=None):
        Client = get_model('client', 'Client')
        qs = self
        if worth is None:
            return self

        clients = [goal.account.primary_owner for goal in qs]
        cmap = {}
        if worth == Client.WORTH_AFFLUENT:
            cmap['affluent'] = [c.id for c in clients if c.get_worth() == Client.WORTH_AFFLUENT]
            # logger.error(cmap['affluent'])
            qs = self.filter(account__primary_owner__in=cmap['affluent'])
        elif worth == Client.WORTH_HIGH:
            cmap['high'] = [c.id for c in clients if c.get_worth() == Client.WORTH_HIGH]
            # logger.error(cmap['high'])
            qs = self.filter(account__primary_owner__in=cmap['high'])
        elif worth == Client.WORTH_VERY_HIGH:
            cmap['very-high'] = [c.id for c in clients if c.get_worth() == Client.WORTH_VERY_HIGH]
            qs = self.filter(account__primary_owner__in=cmap['very-high'])
        elif worth == Client.WORTH_ULTRA_HIGH:
            cmap['ultra-high'] = [c.id for c in clients if c.get_worth() == Client.WORTH_ULTRA_HIGH]
            qs = self.filter(account__primary_owner__in=cmap['ultra-high'])

        return qs


class PositionLotQuerySet(QuerySet):
    def filter_by_firm(self, firm):
        return self.filter(Q(execution_distribution__transaction__from_goal__account__primary_owner__advisor__firm=firm) |
                           Q(execution_distribution__transaction__to_goal__account__primary_owner__advisor__firm=firm))

    def filter_by_advisors(self, advisors):
        q = Q()
        for advisor in advisors:
            q |= Q(execution_distribution__transaction__from_goal__account__primary_owner__advisor=advisor)
            q |= Q(execution_distribution__transaction__to_goal__account__primary_owner__advisor=advisor)
        return self.filter(q)

    def filter_by_clients(self, clients):
        q = Q()
        for client in clients:
            q |= Q(execution_distribution__transaction__from_goal__account__primary_owner=client)
            q |= Q(execution_distribution__transaction__to_goal__account__primary_owner=client)
        return self.filter(q)

    def filter_by_risk_level(self, risk_levels=None):
        if risk_levels is None:
            return self

        from .models import GoalMetric

        if isinstance(risk_levels, int):
            risk_levels = [risk_levels, ]
        else:
            risk_levels = [int(r) for r in risk_levels]

        q = Q()
        for level in risk_levels:
            risk_min, risk_max = GoalMetric.risk_level_range(level)
            q |= Q(execution_distribution__transaction__from_goal__selected_settings__metric_group__metrics__configured_val__gte=risk_min,
                   execution_distribution__transaction__from_goal__selected_settings__metric_group__metrics__configured_val__lt=risk_max)
            q |= Q(execution_distribution__transaction__to_goal__selected_settings__metric_group__metrics__configured_val__gte=risk_min,
                   execution_distribution__transaction__to_goal__selected_settings__metric_group__metrics__configured_val__lt=risk_max)
        qs = self.filter(q, goal__selected_settings__metric_group__metrics__type=GoalMetric.METRIC_TYPE_RISK_SCORE)

        return qs

    def filter_by_worth(self, worth=None):
        Client = get_model('client', 'Client')
        qs = self
        if worth is None:
            return self

        clients = [p.execution_distribution__transaction__to_goal__account__primary_owner for p in qs]
        cmap = {}
        if worth == Client.WORTH_AFFLUENT:
            cmap['affluent'] = [c.id for c in clients if c.get_worth() == Client.WORTH_AFFLUENT]
            qs = self.filter(execution_distribution__transaction__to_goal__account__primary_owner__in=cmap['affluent'])
        elif worth == Client.WORTH_HIGH:
            cmap['high'] = [c.id for c in clients if c.get_worth() == Client.WORTH_HIGH]
            qs = self.filter(execution_distribution__transaction__to_goal__account__primary_owner__in=cmap['high'])
        elif worth == Client.WORTH_VERY_HIGH:
            cmap['very-high'] = [c.id for c in clients if c.get_worth() == Client.WORTH_VERY_HIGH]
            qs = self.filter(execution_distribution__transaction__to_goal__account__primary_owner__in=cmap['very-high'])
        elif worth == Client.WORTH_ULTRA_HIGH:
            cmap['ultra-high'] = [c.id for c in clients if c.get_worth() == Client.WORTH_ULTRA_HIGH]
            qs = self.filter(execution_distribution__transaction__to_goal__account__primary_owner__in=cmap['ultra-high'])
        return qs





class ExternalAssetQuerySet(QuerySet):
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
