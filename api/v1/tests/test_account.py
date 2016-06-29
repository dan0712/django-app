from rest_framework import status
from rest_framework.test import APITestCase

from main.event import Event
from main.models import ClientAccount, ACCOUNT_TYPE_PERSONAL, ActivityLogEvent, AccountTypeRiskProfileGroup
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
        # The account creator gets the risk profile group from the default for the account, so we need to set that up.
        AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_PERSONAL,
                                                   risk_profile_group=Fixture1.risk_profile_group1())
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
