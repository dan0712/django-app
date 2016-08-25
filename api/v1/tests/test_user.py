from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import User
from main.tests.fixtures import Fixture1
from main.constants import ACCOUNT_TYPES
from django.core.urlresolvers import reverse
from .factories import UserFactory, GroupFactory, ClientFactory, RiskProfileGroupFactory, \
    AccountTypeRiskProfileGroupFactory, AddressFactory
from common.constants import GROUP_SUPPORT_STAFF


class UserTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.user = UserFactory.create()

        # Populate the AccountType -> RiskProfileGroup mapping
        for atid, _ in ACCOUNT_TYPES:
            AccountTypeRiskProfileGroupFactory.create(account_type=atid)

        self.user2 = UserFactory.create()
        self.client2 = ClientFactory(user=self.user2, income=5555.01)

        self.client3 = ClientFactory()
        self.client3.user.groups_add(User.GROUP_CLIENT)

    def tearDown(self):
        self.client.logout()

    def test_login(self):
        url = '/api/v1/login'
        usr = Fixture1.client1_user()
        usr.set_password('temppass')
        usr.save()
        data = {
            'username': usr.email,
            'password': 'temppass',
        }
        response = self.client.post(url, data)
        self.assertIn('sessionid', response.cookies)

    def test_get_client_user_settings(self):
        client = ClientFactory(user=self.user)
        client.user.groups_add(User.GROUP_CLIENT)

        url = reverse('api:v1:user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated request to get user settings')
        self.client.force_authenticate(client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated get request to get user settings')

        self.assertTrue(response.data['first_name'] == self.user.first_name)
        self.assertTrue(response.data['id'] == self.user.client.id)
        self.assertTrue(response.data['income'] == self.user.client.income)

        # lets make a new client with a different income and check results on it
        self.user2.groups_add(User.GROUP_CLIENT)
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated get request to get user settings')
        self.assertTrue(response.data['id'] == self.user2.client.id)
        self.assertTrue(response.data['income'] == self.client2.income)

    def test_update_client_user_settings(self):
        # the user must be a client, advisor or possibly supportstaff here, otherwise 403
        client = ClientFactory(user=self.user)
        client.user.groups_add(User.GROUP_CLIENT)

        url = reverse('api:v1:user-me')
        new_name = 'Bruce Wayne'
        data = {
            'first_name': new_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'password': 'test',
            'password2': 'test',
            'oldpassword': 'test',
        }
        # 403 unauthenticated request
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated request to update user settings')

        # 200 for put request
        self.client.force_authenticate(self.user)

        # We gave a get control response so we can compare the two.
        control_response = self.client.get(url)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated put request to update user settings')
        self.assertEqual(len(control_response.data), len(response.data))
        self.assertTrue(response.data['first_name'] == new_name)
        self.assertTrue(response.data['id'] == self.user.client.id)

        # lets test income update
        old_income = self.user.client.income
        new_income = old_income + 5000.0
        new_occupation = 'Super Hero'
        new_employer = 'League of Extraordinary Gentlemen'
        new_civil_status = 1  # 0 single, 1 married
        data = {
            'income': new_income,
            'occupation': new_occupation,
            'employer': new_employer,
            'civil_status': new_civil_status,
            'oldpassword': 'test',
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated put request to update user income, occupation, employer, and civil status')
        self.assertTrue(response.data['id'] == self.user.client.id)
        self.assertTrue(response.data['income'] == new_income)
        self.assertTrue(response.data['occupation'] == new_occupation)
        self.assertTrue(response.data['employer'] == new_employer)
        self.assertTrue(response.data['civil_status'] == new_civil_status)
        control_response = self.client.get(url)
        self.assertTrue(control_response.data['occupation'] == new_occupation)

    def test_update_client_address(self):
        url = reverse('api:v1:user-me')
        # residential_address should be self.client3.residential_address.pk
        self.client.force_authenticate(self.client3.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated put request to get user settings to check address')
        self.assertTrue(response.data['residential_address'] == self.client3.residential_address.pk)

        # lets create a new address
        new_address = AddressFactory.create()
        data = {
            'residential_address': new_address.pk
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated put request to updat user address')
        self.assertTrue(response.data['residential_address'] == new_address.pk)
