from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from api.v1.tests.factories import RetirementPlanFactory, RetirementAdviceFactory, \
    GroupFactory, EmailInviteFactory, GoalFactory, GoalSettingFactory, \
    PortfolioSetFactory, AssetClassFactory, GoalMetricFactory, \
    RecurringTransactionFactory
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from common.constants import GROUP_SUPPORT_STAFF
from retiresmartz.models import RetirementAdvice
from client.models import EmailInvite
from django.utils import timezone
from main.models import Goal, GoalMetric, InvestmentType
from main.risk_profiler import max_risk, MINIMUM_RISK


class RetirementAdviceTests(TestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.plan = RetirementPlanFactory.create()
        # self.advice_url = reverse('api:v1:client-retirement-advice', args=[self.plan.client.id, self.plan.id])
        self.advice_url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed'.format(self.plan.client.id, self.plan.id)

        self.invite = EmailInviteFactory.create(user=self.plan.client.user,
                                                status=EmailInvite.STATUS_ACCEPTED)

        self.bonds_type = InvestmentType.Standard.BONDS.get()
        self.stocks_type = InvestmentType.Standard.STOCKS.get()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=self.bonds_type)
        self.stocks_asset_class = AssetClassFactory.create(investment_type=self.stocks_type)
        self.portfolio_set = PortfolioSetFactory.create()
        self.portfolio_set.asset_classes.add(self.bonds_asset_class, self.stocks_asset_class)

    def test_welcome_back(self):
        """
            On user login through the backend login view,
            if user is a client, RetirementAdvice welcome
            message should be retrievable at the advice endpoint.
        """
        login_url = reverse('login')
        data = {
            'username': self.plan.client.user.email,
            'password': 'test',
        }
        response = self.client.post(login_url, data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['text'], "Hello, welcome back %s" % self.plan.client.user.first_name)

    def test_onboarding_complete(self):
        """
            Onboarding complete advice should pop if
            EmailInvite status is set to STATUS_COMPLETE
            and had previous been set to STATUS_ACCEPTED
        """
        self.invite.status = EmailInvite.STATUS_COMPLETE
        self.invite.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_decrease_retirement_age_to_62(self):
        """
            Onboarding retirement age advice pops
            if user decreases their retirement age to 62.
        """
        self.plan.retirement_age = 63
        self.plan.save()
        # decrease to 62
        self.plan.retirement_age = 62
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 manual age adjustments trigger too
        self.assertEqual(len(response.data['results']), 3)

    def test_decrease_retirement_age_to_63(self):
        """
            Onboarding retirement age advice pops
            if user decreases their retirement age to 63.
        """
        self.plan.retirement_age = 64
        self.plan.save()
        # decrease to 63
        self.plan.retirement_age = 63
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 manual age adjustments trigger too
        self.assertEqual(len(response.data['results']), 3)

    def test_decrease_retirement_age_to_64(self):
        """
            Onboarding retirement age advice pops
            if user decreases their retirement age to 64.
        """
        self.plan.retirement_age = 65
        self.plan.save()
        # decrease to 64
        self.plan.retirement_age = 64
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 manual age adjustments trigger too
        self.assertEqual(len(response.data['results']), 3)

    def test_decrease_retirement_age_to_65(self):
        """
            Onboarding retirement age advice pops
            if user decreases their retirement age to 65.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # decrease to 64
        self.plan.retirement_age = 65
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 manual age adjustments trigger too
        self.assertEqual(len(response.data['results']), 3)

    def test_increase_retirement_age_to_67(self):
        """
            Onboarding retirement age advice pops
            if user increases their retirement age to 67.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # increase to 67
        self.plan.retirement_age = 67
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 manual age adjustments trigger too
        self.assertEqual(len(response.data['results']), 3)

    def test_increase_retirement_age_to_68(self):
        """
            Onboarding retirement age advice pops
            if user increases their retirement age to 68.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # increase to 68
        self.plan.retirement_age = 68
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 manual age adjustments trigger too
        self.assertEqual(len(response.data['results']), 3)

    def test_increase_retirement_age_to_69(self):
        """
            Onboarding retirement age advice pops
            if user increases their retirement age to 69.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # increase to 69
        self.plan.retirement_age = 69
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 manual age adjustments trigger too
        self.assertEqual(len(response.data['results']), 3)

    def test_increase_retirement_age_to_70(self):
        """
            Onboarding retirement age advice pops
            if user increases their retirement age to 70.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # increase to 70
        self.plan.retirement_age = 70
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 manual age adjustments trigger too
        self.assertEqual(len(response.data['results']), 3)

    def test_manually_adjusted_age(self):
        self.plan.retirement_age = 70
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_smoker_yes(self):
        pre_save_count = RetirementAdvice.objects.count()
        self.plan.client.smoker = True
        self.plan.client.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # combination advice and smoker advice
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(RetirementAdvice.objects.count(), pre_save_count + 2)

    def test_smoker_no(self):
        pre_save_count = RetirementAdvice.objects.count()
        self.plan.client.smoker = False
        self.plan.client.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # combination advice and smoker advice
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(RetirementAdvice.objects.count(), pre_save_count + 2)

    def test_exercise_only(self):
        self.plan.client.daily_exercise = 20
        self.plan.client.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_weight_and_height_only(self):
        self.plan.client.weight = 145
        self.plan.client.height = 2
        self.plan.client.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_combination_wellbeing_entries(self):
        self.plan.client.weight = 145
        self.plan.client.height = 2
        self.plan.client.daily_exercise = 20
        self.plan.client.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_all_wellbeing_entries(self):
        self.plan.client.weight = 145
        self.plan.client.height = 2
        self.plan.client.daily_exercise = 20
        self.plan.client.smoker = False
        self.plan.client.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # not smoking advice and all wellbeing entries
        self.assertEqual(len(response.data['results']), 2)

    def test_protective_risk_move(self):

        plan = RetirementPlanFactory.create(desired_risk=.5,
                                            recommended_risk=.5)
        advice_url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed'.format(plan.client.id, plan.id)
        plan.desired_risk = .3
        plan.save()
        login_ok = self.client.login(username=plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_dynamic_risk_move(self):
        plan = RetirementPlanFactory.create(desired_risk=.5,
                                            recommended_risk=.5)
        advice_url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed'.format(plan.client.id, plan.id)
        plan.desired_risk = .8
        plan.save()
        login_ok = self.client.login(username=plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_spending_increased_contributions_decreased(self):
        self.plan.income += 100000
        self.plan.btc -= 10000
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_spending_decreased_contributions_increased(self):
        self.plan.income -= 50000
        self.plan.btc += 10000
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # TODO: Fix Trigger
    def test_plan_off_track_now(self):
        self.plan._on_track = True
        self.plan.save()
        self.plan._on_track = False
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # two advice, one for for getting on track,
        # and one for getting off track
        self.assertEqual(len(response.data['results']), 2)

    def test_plan_on_track_now(self):
        self.plan._on_track = True
        self.plan.save()
        login_ok = self.client.login(username=self.plan.client.user.email, password='test')
        self.assertTrue(login_ok)
        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
