from rest_framework import status
from rest_framework.test import APITestCase

from main.event import Event
from main.models import ActivityLogEvent, ActivityLog, AccountTypeRiskProfileGroup, ACCOUNT_TYPE_PERSONAL, \
    ACCOUNT_TYPE_JOINT, ACCOUNT_TYPE_CORPORATE, ACCOUNT_TYPE_SMSF, ACCOUNT_TYPE_TRUST
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

    def test_account_types_missing(self):
        # Populate some account mappings
        m1 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_PERSONAL,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        url = '/api/v1/settings/account-types'
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_account_types_available(self):
        # Populate some account mappings
        m1 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_PERSONAL,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        m2 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_JOINT,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        m3 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_CORPORATE,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        m4 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_SMSF,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        m5 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_TRUST,
                                                        risk_profile_group=Fixture1.risk_profile_group1())

        url = '/api/v1/settings/account-types'
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]['default_risk_profile_group'], Fixture1.risk_profile_group1().id)
