from rest_framework.test import APITestCase

from main.event import Event
from main.models import ActivityLogEvent, ActivityLog
from main.tests.fixtures import Fixture1


class SettingsTests(APITestCase):
    def test_get_goal_types(self):
        Fixture1.goal_type1()
        url = '/api/v1/settings/goal-types'
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'goaltype1')
        self.assertEqual(response.data[0]['risk_sensitivity'], 7.0)

    def test_get_activity_types(self):
        # Populate some activity type items
        ActivityLog.objects.all().delete()
        ActivityLogEvent.objects.all().delete()
        ActivityLogEvent.get(Event.APPROVE_SELECTED_SETTINGS)
        ActivityLogEvent.get(Event.GOAL_WITHDRAWAL_EXECUTED)

        url = '/api/v1/settings/activity-types'
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
