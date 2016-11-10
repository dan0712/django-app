from datetime import date, datetime
from ujson import loads
from unittest import mock
from unittest.mock import MagicMock

from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import GROUP_SUPPORT_STAFF
from retiresmartz.models import RetirementPlan
from .factories import AssetClassFactory, ContentTypeFactory, GroupFactory, \
    RetirementPlanFactory, TickerFactory, RetirementAdviceFactory
from django.utils import timezone
from api.v1.tests.factories import RetirementPlanFactory, RetirementAdviceFactory, \
    GroupFactory, EmailInviteFactory, GoalFactory, GoalSettingFactory, \
    PortfolioSetFactory, AssetClassFactory, GoalMetricFactory, \
    RecurringTransactionFactory
from rest_framework import status
from django.core.urlresolvers import reverse
from common.constants import GROUP_SUPPORT_STAFF
from retiresmartz.models import RetirementAdvice
from client.models import EmailInvite
from main.models import InvestmentType
mocked_now = datetime(2016, 1, 1)


class RetiresmartzAdviceTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.plan = RetirementPlanFactory.create()
        self.plan2 = RetirementPlanFactory.create(client=self.plan.client)
        self.plan3 = RetirementPlanFactory.create()
        # self.advice_url = reverse('api:v1:client-retirement-advice', args=[self.plan.client.id, self.plan.id])
        self.plan_url = '/api/v1/clients/{}/retirement-plans/{}'.format(self.plan.client.id, self.plan.id)
        self.advice_url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed'.format(self.plan.client.id, self.plan.id)
        self.advice_url2 = '/api/v1/clients/{}/retirement-plans/{}/advice-feed'.format(self.plan2.client.id, self.plan2.id)
        self.client_url = '/api/v1/clients/{}'.format(self.plan.client.id)
        self.invite = EmailInviteFactory.create(user=self.plan.client.user,
                                                status=EmailInvite.STATUS_ACCEPTED)

        self.bonds_type = InvestmentType.Standard.BONDS.get()
        self.stocks_type = InvestmentType.Standard.STOCKS.get()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=self.bonds_type)
        self.stocks_asset_class = AssetClassFactory.create(investment_type=self.stocks_type)
        self.portfolio_set = PortfolioSetFactory.create()
        self.portfolio_set.asset_classes.add(self.bonds_asset_class, self.stocks_asset_class)

    def test_decrease_retirement_age_to_62(self):
        """
            Onboarding retirement age advice pops
            if user decreases their retirement age to 62.
        """
        self.plan.retirement_age = 63
        self.plan.save()
        # decrease to 62
        data = {
            'retirement_age': 62,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_decrease_retirement_age_to_63(self):
        """
            Onboarding retirement age advice pops
            if user decreases their retirement age to 63.
        """
        self.plan.retirement_age = 64
        self.plan.save()
        # decrease to 63
        data = {
            'retirement_age': 63,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_decrease_retirement_age_to_64(self):
        """
            Onboarding retirement age advice pops
            if user decreases their retirement age to 64.
        """
        self.plan.retirement_age = 65
        self.plan.save()
        # decrease to 64
        data = {
            'retirement_age': 64,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_decrease_retirement_age_to_65(self):
        """
            Onboarding retirement age advice pops
            if user decreases their retirement age to 65.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # decrease to 65
        data = {
            'retirement_age': 65,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_increase_retirement_age_to_67(self):
        """
            Onboarding retirement age advice pops
            if user increases their retirement age to 67.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # increase to 67
        data = {
            'retirement_age': 67,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_increase_retirement_age_to_68(self):
        """
            Onboarding retirement age advice pops
            if user increases their retirement age to 68.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # increase to 68
        data = {
            'retirement_age': 68,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_increase_retirement_age_to_69(self):
        """
            Onboarding retirement age advice pops
            if user increases their retirement age to 69.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # increase to 69
        data = {
            'retirement_age': 69,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_increase_retirement_age_to_70(self):
        """
            Onboarding retirement age advice pops
            if user increases their retirement age to 70.
        """
        self.plan.retirement_age = 66
        self.plan.save()
        # increase to 70
        data = {
            'retirement_age': 70,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_manually_adjusted_age(self):
        self.plan.retirement_age = 70
        self.plan.save()
        data = {
            'selected_life_expectancy': 59,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_smoker_yes(self):
        pre_save_count = RetirementAdvice.objects.count()
        data = {
            'smoker': True,
        }
        prev_life_expectancy = self.plan2.selected_life_expectancy
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.client_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # combination advice and smoker advice
        lookup_advice = RetirementAdvice.objects.get(plan=self.plan2)
        self.assertEqual(response.data['results'][0]['id'], lookup_advice.id)
        self.assertEqual(response.data['results'][0]['plan'], self.plan2.id)

    def test_smoker_no(self):
        pre_save_count = RetirementAdvice.objects.count()
        self.plan2.selected_life_expectancy = 80
        data = {
            'smoker': False,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.client_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # combination advice and smoker advice
        lookup_advice = RetirementAdvice.objects.get(plan=self.plan)
        self.assertEqual(response.data['results'][0]['id'], lookup_advice.id)
        self.assertEqual(response.data['results'][0]['plan'], self.plan.id)
        lookup_plan = RetirementPlan.objects.get(pk=self.plan2.id)
        self.assertEqual(lookup_plan.selected_life_expectancy, 87)

    def test_exercise_only(self):
        data = {
            'daily_exercise': 20,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.client_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_weight_and_height_only(self):
        data = {
            'weight': 145,
            'height': 2,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.client_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_weight_only(self):
        data = {
            'weight': 145,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.client_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_height_only(self):
        data = {
            'height': 9,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.client_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # def test_combination_wellbeing_entries(self):
    #     data = {
    #         'weight': 145,
    #         'height': 2,
    #         'daily_exercise': 20,
    #     }
    #     self.client.force_authenticate(user=self.plan.client.user)
    #     response = self.client.put(self.client_url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    #     response = self.client.get(self.advice_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['results']), 3)

    def test_all_wellbeing_entries(self):
        data = {
            'weight': 145,
            'height': 2,
            'daily_exercise': 20,
            'smoker': False,
            'drinks': 5,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.client_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_protective_risk_move(self):
        plan = RetirementPlanFactory.create(desired_risk=.5,
                                            recommended_risk=.5)
        plan_url = '/api/v1/clients/{}/retirement-plans/{}'.format(plan.client.id, plan.id)
        advice_url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed'.format(plan.client.id, plan.id)
        data = {
            'desired_risk': .01,
        }
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.put(plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_dynamic_risk_move(self):
        plan = RetirementPlanFactory.create(desired_risk=.5,
                                            recommended_risk=.5)
        plan_url = '/api/v1/clients/{}/retirement-plans/{}'.format(plan.client.id, plan.id)
        advice_url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed'.format(plan.client.id, plan.id)
        data = {
            'desired_risk': .8,
        }
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.put(plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_spending_increased_contributions_decreased(self):
        data = {
            'btc': 1,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_spending_decreased_contributions_increased(self):
        data = {
            'btc': 10000,
        }
        self.client.force_authenticate(user=self.plan.client.user)
        response = self.client.put(self.plan_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(self.advice_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    # TODO: Need to trigger track changes with put here
    # Once task to make RetirementPlan on_track actually work
    # is complete, then these tests can be implemented
    # Triggers are already in place
    # def test_plan_off_track_now(self):
    #     self.plan._on_track = True
    #     self.plan.save()
    #     self.plan._on_track = False
    #     self.plan.save()
    #     self.client.force_authenticate(user=self.plan.client.user)

    #     response = self.client.get(self.advice_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['results']), 1)

    # def test_plan_on_track_now(self):
    #     self.plan._on_track = True
    #     self.plan.save()
    #     self.client.force_authenticate(user=self.plan.client.user)
    #     response = self.client.get(self.advice_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['results']), 1)
