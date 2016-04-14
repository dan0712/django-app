from django.db import models
from django.db.models.query_utils import Q


class ClientQuerySet(models.query.QuerySet):
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
            Q(secondary_advisors__id=advisor.id)
        )

    def filter_by_client(self, client):
        """
        A client is only allowed to see its own record.
        :param client:
        :return:
        """
        return self.filter(id=client.id)


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
            Q(primary_owner__secondary_advisors__id=advisor.id) |
            Q(signatories__advisor=advisor) |
            Q(signatories__secondary_advisors__id=advisor.id) |
            Q(account_group__advisor=advisor) |
            Q(account_group__secondary_advisors__id=advisor.id)
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
            Q(signatories__id=client.id)
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
            Q(account__primary_owner__secondary_advisors__id=advisor.id) |
            Q(account__signatories__advisor=advisor) |
            Q(account__signatories__secondary_advisors__id=advisor.id) |
            Q(account__account_group__advisor=advisor) |
            Q(account__account_group__secondary_advisors__id=advisor.id)
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
            Q(account__signatories__id=client.id)
        )
