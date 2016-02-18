from django.db import models


class ClientAccountQuerySet(models.query.QuerySet):
    def filter_by_firm(self, firm):
        """
        Experimental
        """
        qs = self.filter(account_group__advisor__firm=firm.pk)
        return qs

    def filter_by_advisor(self, advisor):
        """
        Experimental
        could be renamed to "filter_by_advisor_permissions"
        in case of naming collisions
        """
        # TODO: should we add here "secondary_advisors"?
        qs = self.filter(account_group__advisor=advisor.pk)

        return qs

    def filter_by_client(self, client):
        """
        Experimental
        """
        qs = self.filter(primary_owner=client.pk)
        return qs


class GoalQuerySet(models.query.QuerySet):
    def filter_by_firm(self, firm):
        """
        Experimental
        """
        qs = self.filter(account__account_group__advisor__firm=firm.pk)
        return qs

    def filter_by_advisor(self, advisor):
        """
        Experimental
        could be renamed to "filter_by_advisor_permissions"
        in case of naming collisions
        """
        # TODO: should we add here "secondary_advisors"?
        qs = self.filter(account__account_group__advisor=advisor.pk)

        return qs

    def filter_by_client(self, client):
        """
        Experimental
        """
        qs = self.filter(account__primary_owner=client.pk)
        return qs
