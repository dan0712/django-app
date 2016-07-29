from rest_framework import status
from rest_framework.test import APITestCase

from client.models import AccountTypeRiskProfileGroup
from main.constants import ACCOUNT_TYPE_CORPORATE, ACCOUNT_TYPE_JOINT, \
    ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_SMSF, ACCOUNT_TYPE_TRUST
from main.event import Event
from main.models import ActivityLog, ActivityLogEvent
from main.tests.fixtures import Fixture1


class SettingsTests(APITestCase):
    def test_get_goal_types(self):
        Fixture1.goal_type1()
        url = '/api/v1/settings/goal-types'
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'goaltype1')
        self.assertFalse('risk_sensitivity' in response.data[0])  # We should not make public our risk model.

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

    def test_account_types(self):
        # Populate one (not all) of the account mappings
        m1 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_PERSONAL,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        url = '/api/v1/settings/account-types'
        self.client.force_authenticate(user=Fixture1.client1().user)

        # Make sure we have a problem when getting the account types.
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Populate the rest of the account mappings
        m2 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_JOINT,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        m3 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_CORPORATE,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        m4 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_SMSF,
                                                        risk_profile_group=Fixture1.risk_profile_group1())
        m5 = AccountTypeRiskProfileGroup.objects.create(account_type=ACCOUNT_TYPE_TRUST,
                                                        risk_profile_group=Fixture1.risk_profile_group1())

        # Make sure all ok now.
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]['default_risk_profile_group'], Fixture1.risk_profile_group1().id)

    def test_all_settings(self):
        # Populate a goal type
        gt = Fixture1.goal_type1()

        # Populate all of the account mappings
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

        url = '/api/v1/settings'
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Make sure the goal types are there
        self.assertEqual(len(response.data['goal_types']), 1)
        self.assertEqual(response.data['goal_types'][0]['name'], 'goaltype1')

        # Make sure the civil_statuses are there
        self.assertTrue('civil_statuses' in response.data)
        self.assertEqual(set(('id', 'name')), set(response.data['civil_statuses'][0].keys()))

        # Make sure the employment_statuses are there
        self.assertTrue('employment_statuses' in response.data)
        self.assertEqual(set(('id', 'name')), set(response.data['employment_statuses'][0].keys()))

        # Make sure the external_asset_types are there
        self.assertTrue('external_asset_types' in response.data)
        self.assertEqual(set(('id', 'name')), set(response.data['external_asset_types'][0].keys()))
