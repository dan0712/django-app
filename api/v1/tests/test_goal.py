from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase

from main.event import Event
from main.models import ActivityLogEvent, DailyPrice, ClientAccount, MarketOrderRequest
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

    def test_performance_history_empty(self):
        url = '/api/v1/goals/{}/performance-history'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_performance_history(self):
        prices = (
            (Fixture1.fund1(), '20160101', 10),
            (Fixture1.fund1(), '20160102', 10.5),
            (Fixture1.fund1(), '20160103', 10.6),
            (Fixture1.fund1(), '20160104', 10.3),
            (Fixture1.fund1(), '20160105', 10.1),
            (Fixture1.fund1(), '20160106', 9.9),
            (Fixture1.fund1(), '20160107', 10.5),
            (Fixture1.fund2(), '20160101', 50),
            (Fixture1.fund2(), '20160102', 51),
            (Fixture1.fund2(), '20160103', 53),
            (Fixture1.fund2(), '20160104', 53.5),
            (Fixture1.fund2(), '20160105', 51),
            (Fixture1.fund2(), '20160106', 52),
            (Fixture1.fund2(), '20160107', 51.5),
        )
        Fixture1.set_prices(prices)

        order_details = (
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
            (Fixture1.personal_account1(), MarketOrderRequest.State.COMPLETE),
        )
        orders = Fixture1.add_orders(order_details)

        execution_details = (
            (Fixture1.fund1(), orders[0], 3, 10.51, -75, '20160102'),
            (Fixture1.fund1(), orders[0], 4, 10.515, -75.05, '20160102'),
            (Fixture1.fund1(), orders[1], -1, 10.29, 10, '20160104'),
            (Fixture1.fund2(), orders[2], 2, 53.49, -110, '20160104'),
            (Fixture1.fund2(), orders[2], 8, 53.5, -430, '20160104'),
            (Fixture1.fund1(), orders[3], -3, 10.05, 30, '20160105'),
            (Fixture1.fund2(), orders[4], -3, 50.05, 145, '20160105'),
            (Fixture1.fund2(), orders[4], -2, 50.04, 98, '20160105'),
            (Fixture1.fund2(), orders[5], -5, 52, 255, '20160106'),
        )
        executions = Fixture1.add_executions(execution_details)

        # We distribute the entire executions to one goal.
        distributions = (
            (executions[0], 3, Fixture1.goal1()),
            (executions[1], 4, Fixture1.goal1()),
            (executions[2], -1, Fixture1.goal1()),
            (executions[3], 2, Fixture1.goal1()),
            (executions[4], 8, Fixture1.goal1()),
            (executions[5], -3, Fixture1.goal1()),
            (executions[6], -3, Fixture1.goal1()),
            (executions[7], -2, Fixture1.goal1()),
            (executions[8], -5, Fixture1.goal1()),
        )
        Fixture1.add_execution_distributions(distributions)

        url = '/api/v1/goals/{}/performance-history'.format(Fixture1.goal1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0], (16802, 0))  # 20160102
        self.assertEqual(response.data[1], (16803, Decimal('0.009524')))
        self.assertEqual(response.data[2], (16804, Decimal('-0.028302')))
        self.assertEqual(response.data[3], (16805, Decimal('-0.043901')))
        self.assertEqual(response.data[4], (16806, Decimal('-0.019802')))
        self.assertEqual(response.data[5], (16807, Decimal('0.060606')))
        self.assertEqual(response.data[6], (16808, 0))
