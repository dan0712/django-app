from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import GROUP_SUPPORT_STAFF
from main.constants import ACCOUNT_TYPES
from main.models import User
from main.tests.fixture import Fixture1
from .factories import AccountTypeRiskProfileGroupFactory, ClientFactory, \
    GroupFactory, UserFactory


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
        self.assertTrue(response.data['id'] == self.user.id)
        self.assertTrue(response.data['client']['id'] == self.user.client.id)
        self.assertTrue(response.data['client']['income'] == self.user.client.income)

        # lets make a new client with a different income and check results on it
        self.user2.groups_add(User.GROUP_CLIENT)
        self.client.force_authenticate(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated get request to get user settings')
        self.assertTrue(response.data['id'] == self.user2.id)
        self.assertTrue(response.data['client']['id'] == self.client2.id)
        self.assertTrue(response.data['client']['income'] == self.client2.income)
        self.assertEqual(response.data['client']['residential_address']['address'],
                         self.client2.residential_address.address)

    def test_update_user_settings(self):
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

        self.client.force_authenticate(self.user)

        response = self.client.put(url, data)
        # We gave a get control response so we can compare the two.
        control_response = self.client.get(url)
        # 200 for put request
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated put request to update user settings')
        # MAke sure put and get return same data
        self.assertEqual(control_response.data, response.data)
        self.assertEqual(response.data['first_name'], new_name)
        self.assertEqual(response.data['id'], self.user.id)

    def test_phone_number_valid(self):
        url = reverse('api:v1:phonenumber-validation')
        data = {
            'number': '15592467777',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='Unauthenticated phone number validation fails')

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Authenticated valid phone number returns 200')

    def test_phone_number_invalid(self):
        url = reverse('api:v1:phonenumber-validation')
        data = {
            'number': '15555555555',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='Unauthenticated phone number validation fails')

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='Authenticated invalid phone number validation returns 400')

    def test_phone_number_with_symbols(self):
        url = reverse('api:v1:phonenumber-validation')
        data = {
            'number': '+1-234-234-2342',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='Unauthenticated phone number validation fails')

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Authenticated valid phone number with + and - symbols returns 200')
