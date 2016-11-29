from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from client.models import AccountTypeRiskProfileGroup, RiskCategory
from main.constants import ACCOUNT_TYPE_CORPORATE, ACCOUNT_TYPE_JOINT, \
    ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_SMSF, ACCOUNT_TYPE_TRUST, ACCOUNT_TYPE_ROTH401K
from main.event import Event
from main.models import ActivityLog, ActivityLogEvent, AccountType
from main.tests.fixture import Fixture1
from common.constants import GROUP_SUPPORT_STAFF
from api.v1.tests.factories import MarketIndexFactory, TickerFactory, AssetFeatureFactory, GroupFactory, \
    InvestmentType, PortfolioSetFactory, AssetClassFactory, AssetFeatureValueFactory, \
    EmailInviteFactory, RiskProfileGroupFactory, GoalSettingFactory
from main.models import GoalMetric, AssetFeature, Ticker
from unittest import mock
from unittest.mock import MagicMock
from django.utils import timezone
from datetime import datetime
from client.models import EmailInvite

mocked_now = datetime(2016, 1, 1)


class SettingsTests(APITestCase):

    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.personal_account_type = AccountType.objects.create(id=ACCOUNT_TYPE_PERSONAL)
        self.r401k_account_type = AccountType.objects.create(id=ACCOUNT_TYPE_ROTH401K)
        self.bonds_type = InvestmentType.Standard.BONDS.get()
        self.stocks_type = InvestmentType.Standard.STOCKS.get()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=self.bonds_type)
        self.stocks_asset_class = AssetClassFactory.create(investment_type=self.stocks_type)
        self.portfolio_set = PortfolioSetFactory.create()
        self.portfolio_set.asset_classes.add(self.bonds_asset_class, self.stocks_asset_class)

        self.risk_score_metric = {
            "type": GoalMetric.METRIC_TYPE_RISK_SCORE,
            "comparison": GoalMetric.METRIC_COMPARISON_EXACTLY,
            "configured_val": 0.4,
            "rebalance_type": GoalMetric.REBALANCE_TYPE_RELATIVE,
            "rebalance_thr": 0.1
        }
        self.bonds_index = MarketIndexFactory.create()
        self.stocks_index = MarketIndexFactory.create()
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark=self.bonds_index)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark=self.stocks_index)

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
        url = '/api/v1/settings/account-types'
        self.client.force_authenticate(user=Fixture1.client1().user)

        # Before populating any account types for the firm, they are returned as empty.
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # Populate some and we should get them back
        Fixture1.client1().advisor.firm.account_types.add(self.personal_account_type)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['creatable'], True)

    def test_account_types_non_creatable(self):
        url = '/api/v1/settings/account-types'
        self.client.force_authenticate(user=Fixture1.client1().user)

        # Populate a non-creatable and check
        Fixture1.client1().advisor.firm.account_types.add(self.r401k_account_type)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['creatable'], False)

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

    def test_inactive_tickers_not_in_settings(self):
        """
        Make sure inactive tickers are not returned by the /api/v1/settings endpoint
        """
        url = '/api/v1/settings'
        self.bonds_ticker.state = Ticker.State.CLOSED.value
        self.bonds_ticker.save()
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data['tickers'])
        ticker_ids = [int(t['id']) for t in response.data['tickers']]
        self.assertTrue(self.bonds_ticker.id not in ticker_ids)

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_only_active_asset_features_in_settings(self):
        """
            Should only return asset features values
            for active Ticker assets where we have funds.
        """
        url = '/api/v1/settings/asset-features'

        # add some assets
        self.bonds_ticker.state = 1
        self.bonds_ticker.save()

        # Add some asset features that have no values, and some feature values that have no assets.
        # They should also not be included.
        orphan_feature = AssetFeatureFactory.create()
        orphan_feature_value = AssetFeatureValueFactory.create()

        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        inactive_asset_feature = [af for af in AssetFeature.objects.all() if not af.active]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), AssetFeature.objects.count() - len(inactive_asset_feature))
        self.assertTrue(orphan_feature.id not in [f['id'] for f in response.data])
        for f in response.data:
            for fv in f['values']:
                self.assertNotEqual(fv['id'], orphan_feature_value.id, msg='Orphaned feature value in setting endpoint')

    def test_get_investor_risk_categories(self):
        RiskCategory.objects.create(name='Ripping', upper_bound=0.7)

        url = '/api/v1/settings/investor-risk-categories'
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Ripping')
        self.assertEqual(response.data[0]['upper_bound'], 0.7)

    def test_get_risk_profile_groups(self):
        """
        Should be accessible by clients and onboarding users.
        """
        # Bring an invite key, get logged in as a new user
        PW = 'testpassword'
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT)

        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'password': PW,
            'question_one': 'what is the first answer?',
            'question_one_answer': 'answer one',
            'question_two': 'what is the second answer?',
            'question_two_answer': 'answer two',
        }

        # Accept an invitation and create a user
        response = self.client.post(url, data)
        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        invite_detail_url = reverse('api:v1:invite-detail', kwargs={'invite_key': invite.invite_key} )
        me_url = reverse('api:v1:user-me')
        self.assertEqual(EmailInvite.STATUS_ACCEPTED, lookup_invite.status)

        # New user must be logged in and able to see invite data
        self.assertIn('sessionid', response.cookies)
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='/api/v1/me should be valid during invitation')

        # can retrieve risk-profile-groups
        url = '/api/v1/settings/risk-profile-groups'
        group = RiskProfileGroupFactory.create()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], group.name)
