from rest_framework import status
from rest_framework.test import APITestCase
from main.models import ClientAccount, ACCOUNT_TYPE_PERSONAL
from main.tests.fixtures import Fixture1


class AccountTests(APITestCase):
    def test_create_account(self):
        url = '/api/v1/accounts'
        data = {
            'account_type': ACCOUNT_TYPE_PERSONAL,
            'account_name': 'Test Account',
            'primary_owner': Fixture1.client1().id,
        }
        old_count = ClientAccount.objects.count()
        self.client.force_authenticate(user=Fixture1.client1_user())
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClientAccount.objects.count(), old_count + 1)
        self.assertTrue('id' in response.data)
        self.assertEqual(response.data['account_name'], 'Test Account')

    def test_update_account(self):
        url = '/api/v1/accounts/' + str(Fixture1.personal_account1().id)
        test_name = 'Holy Pingalicious Test Account'
        self.assertNotEqual(Fixture1.personal_account1().account_name, test_name)
        data = {
            'account_name': test_name,
        }
        old_count = ClientAccount.objects.count()
        self.client.force_authenticate(user=Fixture1.client1_user())
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ClientAccount.objects.count(), old_count)  # No extra account created
        self.assertTrue('id' in response.data)  # Correct response serializer used
        self.assertEqual(response.data['account_name'], test_name)  # New value returned
        self.assertEqual(Fixture1.personal_account1().account_name, test_name)  # Value in db actually changed
