from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import GROUP_SUPPORT_STAFF
from main.constants import ACCOUNT_TYPES
from main.models import User
from .factories import AccountTypeRiskProfileGroupFactory, ClientFactory, \
    GroupFactory, UserFactory, FirmFactory, AuthorisedRepresentativeFactory, \
    AdvisorFactory, SupervisorFactory


class FirmTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)

        self.firm = FirmFactory.create()

        # having to manually set the private attributes here, some problem with
        # factory_boy not triggering the hasattr checks properly otherwise
        self.authorised_rep = AuthorisedRepresentativeFactory.create(firm=self.firm)
        self.authorised_rep.user._is_authorised_representative = True
        self.authorised_rep.user.save()
        self.advisor = AdvisorFactory.create(firm=self.firm)
        self.advisor.user._is_advisor = True
        self.advisor.user.save()
        self.betasmartz_client = ClientFactory.create(advisor=self.advisor)
        self.betasmartz_client.user._is_client = True
        self.betasmartz_client.user.save()
        self.supervisor = SupervisorFactory.create(firm=self.firm)
        self.supervisor.user._is_supervisor = True
        self.supervisor.user.save()

        self.other_firm = FirmFactory.create()

    def test_get_firm_unauthenticated(self):
        url = reverse('api:v1:firm-single', args=[self.firm.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_firm_as_authorised_representative(self):
        url = reverse('api:v1:firm-single', args=[self.firm.pk])
        self.client.force_authenticate(self.authorised_rep.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Can retrieve /api/v1/firm/<pk> as a firm authorised representative')
        self.assertEqual(self.firm.id, response.data.get('id'))

    def test_get_firm_as_advisor(self):
        url = reverse('api:v1:firm-single', args=[self.firm.pk])
        self.client.force_authenticate(self.advisor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        msg='Can retrieve /api/v1/firm/<pk> as a firm advisor')
        self.assertEqual(self.firm.id, response.data.get('id'))

    def test_get_firm_as_supervisor(self):
        url = reverse('api:v1:firm-single', args=[self.firm.pk])
        self.client.force_authenticate(self.supervisor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        msg='Can retrieve /api/v1/firm/<pk> as a firm supervisor')
        self.assertEqual(self.firm.id, response.data.get('id'))

    def test_get_firm_as_client(self):
        url = reverse('api:v1:firm-single', args=[self.firm.pk])
        self.client.force_authenticate(self.betasmartz_client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Can retrieve /api/v1/firm/<pk> as a firm client')
        self.assertEqual(self.firm.id, response.data.get('id'))

    def test_get_other_firm(self):
        """
        Test that attempts to retrieve firm info that an
        authorised representative, advisor, supervisor
        and/or client is not a part of fails.
        """
        url = reverse('api:v1:firm-single', args=[self.other_firm.pk])
        self.client.force_authenticate(self.authorised_rep.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='Attempt to get firm info fails as authorised representative of another firm')

        self.client.force_authenticate(self.advisor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='Attempt to get firm info fails as advisor of another firm')

        self.client.force_authenticate(self.supervisor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='Attempt to get firm info fails as supervisor of another firm')

        self.client.force_authenticate(self.betasmartz_client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='Attempt to get firm info fails as client of another firm')
