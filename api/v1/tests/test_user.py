from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import User
from main.tests.fixtures import Fixture1
from main.constants import ACCOUNT_TYPES
from django.core.urlresolvers import reverse
from .factories import UserFactory, GroupFactory, ClientFactory, RiskProfileGroupFactory, \
    AccountTypeRiskProfileGroupFactory
from common.constants import GROUP_SUPPORT_STAFF


class UserTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.user = UserFactory.create()

        # Populate the AccountType -> RiskProfileGroup mapping
        for atid, _ in ACCOUNT_TYPES:
            AccountTypeRiskProfileGroupFactory.create(account_type=atid)

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

    def test_update_user_settings(self):
        # the user must be a client, advisor or possibly supportstaff here, otherwise 403
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
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for authenticated put request to update user settings')

        self.assertTrue(response.data['first_name'] == new_name)
        self.assertTrue(response.data['id'] == self.user.id)
