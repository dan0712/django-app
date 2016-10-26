# test mailgun email
from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from api.v1.tests.factories import ClientAccountFactory, GroupFactory, \
    AuthorisedRepresentativeFactory, ClientFactory, AdvisorFactory, \
    AccountGroupFactory
from common.constants import GROUP_SUPPORT_STAFF


class FirmOverviewAdvisorsTests(TestCase):

    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.account = ClientAccountFactory.create()

        self.advisor = self.account.primary_owner.advisor
        self.firm = self.advisor.firm
        self.advisor2 = AdvisorFactory.create(firm=self.firm)
        self.betasmartz_client2 = ClientFactory.create(advisor=self.advisor2)
        self.account2 = ClientAccountFactory.create(primary_owner=self.betasmartz_client2)
        self.account_group = AccountGroupFactory.create(advisor=self.advisor)
        self.account_group2 = AccountGroupFactory.create(advisor=self.advisor2)
        self.account.account_group = self.account_group
        self.account.save()
        self.account2.account_group = self.account_group2
        self.account2.save()
        self.rep = AuthorisedRepresentativeFactory.create(firm=self.firm)

    def test_client_accounts_multiple_advisors(self):
        url = reverse('firm:overview-advisor', args=[self.advisor.pk])
        login = self.client.login(username=self.rep.email, password='test')
        self.assertTrue(login)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.content)
        self.assertTrue(self.account.primary_owner.user.get_full_name() in str(response.content))

        url = reverse('firm:overview-advisor', args=[self.advisor2.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.account2.primary_owner.user.get_full_name() in str(response.content))
