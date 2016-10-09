from rest_framework import status
from rest_framework.test import APITestCase

from client.models import AccountTypeRiskProfileGroup, ClientAccount
from common.constants import GROUP_SUPPORT_STAFF
from main import constants
from main.constants import ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_ROTH401K
from main.event import Event
from main.models import ActivityLogEvent, AccountType
from main.tests.fixture import Fixture1
from .factories import GroupFactory


class AccountTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.personal_account_type = AccountType.objects.create(id=constants.ACCOUNT_TYPE_PERSONAL)
        self.roth401k = AccountType.objects.create(id=constants.ACCOUNT_TYPE_ROTH401K)

    def test_create_account(self):
        url = '/api/v1/accounts'
        client = Fixture1.client1()
        data = {
            'account_type': ACCOUNT_TYPE_PERSONAL,
            'account_name': 'Test Account',
            'primary_owner': client.id,
        }
        old_count = ClientAccount.objects.count()
        self.client.force_authenticate(user=Fixture1.client1_user())
        response = self.client.post(url, data)

        # First off, the test should fail, as personal accounts are not activated for the firm yet.
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Add the personal account type, then the post should succeed
        Fixture1.client1().advisor.firm.account_types.add(self.personal_account_type)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClientAccount.objects.count(), 1)
        self.assertTrue('id' in response.data)
        self.assertEqual(response.data['account_name'], 'Test Account')

        # Don't let them create a second personal account
        data = {
            'account_type': ACCOUNT_TYPE_PERSONAL,
            'account_name': 'Test Account 2',
            'primary_owner': client.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(ClientAccount.objects.count(), 1)

    def test_create_us_retirement_fail(self):
        Fixture1.client1().advisor.firm.account_types.add(self.roth401k)
        url = '/api/v1/accounts'
        client = Fixture1.client1()
        data = {
            'account_type': ACCOUNT_TYPE_ROTH401K,
            'account_name': 'Test Failing Account',
            'primary_owner': client.id,
        }
        self.client.force_authenticate(user=Fixture1.client1_user())
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue('are not user creatable' in str(response.content))

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

    def test_get_no_activity(self):
        url = '/api/v1/accounts/{}/activity'.format(Fixture1.personal_account1().id)
        self.client.force_authenticate(user=Fixture1.client1_user())
        response = self.client.get(url)
        self.assertEqual(response.data, [])

    def test_get_all_activity(self):
        # First add some transactions, balances and eventlogs, and make sure the ActivityLogs are set
        Fixture1.settings_event1()
        Fixture1.transaction_event1()
        Fixture1.populate_balance1() # 2 Activity lines
        ActivityLogEvent.get(Event.APPROVE_SELECTED_SETTINGS)
        ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED)
        ActivityLogEvent.get(Event.GOAL_DEPOSIT_EXECUTED)

        url = '/api/v1/accounts/{}/activity'.format(Fixture1.personal_account1().id)
        self.client.force_authenticate(user=Fixture1.client1_user())
        response = self.client.get(url)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data[0], {'goal': 1,
                                            'time': 946684800,
                                            'type': ActivityLogEvent.get(Event.APPROVE_SELECTED_SETTINGS).activity_log.id})  # Setting change
        self.assertEqual(response.data[1], {'balance': 0.0,
                                            'time': 978220800,
                                            'type': ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED).activity_log.id}) # Balance
        self.assertEqual(response.data[2], {'data': [3000.0],
                                            'goal': 1,
                                            'time': 978307200,
                                            'type': ActivityLogEvent.get(Event.GOAL_DEPOSIT_EXECUTED).activity_log.id}) # Deposit
        self.assertEqual(response.data[3], {'balance': 3000.0,
                                            'time': 978307200,
                                            'type': ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED).activity_log.id}) # Balance
