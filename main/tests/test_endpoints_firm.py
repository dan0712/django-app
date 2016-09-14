from rest_framework import status
from api.v1.tests.factories import ClientAccountFactory, \
    ClientFactory, GoalFactory, \
    TransactionFactory, AccountTypeRiskProfileGroupFactory, \
    ExternalAssetFactory, PositionFactory, TickerFactory, \
    SupervisorFactory, AuthorisedRepresentativeFactory, GroupFactory
from main import constants
from main.models import Supervisor
from django.test import TestCase
from common.constants import GROUP_SUPPORT_STAFF


class FirmEndpointsTests(TestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        # Populate the AccountType -> RiskProfileGroup mapping
        for atid, _ in constants.ACCOUNT_TYPES:
            AccountTypeRiskProfileGroupFactory.create(account_type=atid)

    def test_delete_supervisor_get(self):
        supervisor = SupervisorFactory.create()
        rep = AuthorisedRepresentativeFactory.create(firm=supervisor.firm)
        url = '/firm/supervisors/{}/delete'.format(supervisor.id)
        # unauthenticated
        response = self.client.get(url)
        # redirects to login
        self.assertEqual(response.status_code, status.HTTP_302_FOUND,
                         msg='Unauthenticated get request to get supervisor delete view')

        # authenticated
        self.client.login(username=rep.user.email, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Valid get request to delete view for supervisor')

    def test_delete_supervisor_post(self):
        num_of_supervisors = Supervisor.objects.count()
        supervisor = SupervisorFactory.create()
        self.assertEqual(Supervisor.objects.count(), num_of_supervisors + 1)
        rep = AuthorisedRepresentativeFactory.create(firm=supervisor.firm)
        url = '/firm/supervisors/{}/delete'.format(supervisor.id)

        # unauthenticated
        response = self.client.post(url)
        # redirects to login
        self.assertEqual(response.status_code, status.HTTP_302_FOUND,
                         msg='Unauthenticated post request to supervisor delete view')

        self.client.login(username=rep.user.email, password='test')
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Valid post request to supervisor delete view')

        self.assertEqual(Supervisor.objects.count(), num_of_supervisors)
