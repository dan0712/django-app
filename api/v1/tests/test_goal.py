from rest_framework import status
from rest_framework.test import APITestCase

from main.event import Event
from main.models import ActivityLogEvent
from main.tests.fixtures import Fixture1


class GoalTests(APITestCase):
    def test_get_no_activity(self):
        url = '/api/v1/goals/{}/activity'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_all_activity(self):
        # First add some transactions, balances and eventlogs, and make sure the ActivityLogs are set.
        Fixture1.settings_event1()
        Fixture1.transaction_event1()
        Fixture1.populate_balance1()  # 2 Activity lines
        ActivityLogEvent.get(Event.APPROVE_SELECTED_SETTINGS)
        ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED)
        ActivityLogEvent.get(Event.GOAL_DEPOSIT_EXECUTED)

        url = '/api/v1/goals/{}/activity'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        # Note the Goal not included in response as it is in request.
        self.assertEqual(response.data[0], {'time': 946684800,
                                            'type': ActivityLogEvent.get(Event.APPROVE_SELECTED_SETTINGS).activity_log.id})  # Setting change approval
        self.assertEqual(response.data[1], {'balance': 0.0,
                                            'time': 978220800,
                                            'type': ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED).activity_log.id})  # Balance
        # Deposit. Note inclusion of amount, as we're looking at it from the goal perspective.
        self.assertEqual(response.data[2], {'amount': 3000.0,
                                            'data': [3000.0],
                                            'time': 978307200,
                                            'type': ActivityLogEvent.get(Event.GOAL_DEPOSIT_EXECUTED).activity_log.id})
        self.assertEqual(response.data[3], {'balance': 3000.0,
                                            'time': 978307200,
                                            'type': ActivityLogEvent.get(Event.GOAL_BALANCE_CALCULATED).activity_log.id})  # Balance
