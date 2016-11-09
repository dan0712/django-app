from datetime import date, datetime
from ujson import loads
from unittest import mock
from unittest.mock import MagicMock

from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APITestCase

from api.v1.tests.factories import ExternalAssetFactory, MarkowitzScaleFactory, MarketIndexFactory, \
    PortfolioSetFactory, RetirementStatementOfAdviceFactory
from common.constants import GROUP_SUPPORT_STAFF
from main.management.commands.populate_test_data import populate_prices, populate_cycle_obs, populate_cycle_prediction, \
    populate_inflation
from main.models import InvestmentType, GoalSetting, GoalMetricGroup, GoalMetric
from main.tests.fixture import Fixture1
from retiresmartz.models import RetirementPlan
from .factories import AssetClassFactory, ContentTypeFactory, GroupFactory, \
    RetirementPlanFactory, TickerFactory, RetirementAdviceFactory
from django.utils import timezone
from pinax.eventlog.models import log

mocked_now = datetime(2016, 1, 1)


class RetiresmartzTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.base_plan_data = {
            "name": "Personal Plan",
            "description": "My solo plan",
            'desired_income': 60000,
            'income': 80000,
            'volunteer_days': 1,
            'paid_days': 2,
            'same_home': True,
            'reverse_mortgage': True,
            'expected_return_confidence': 0.5,
            'max_employer_match_percent': 0.04,
        }

    def tearDown(self):
        self.client.logout()

    def test_get_plan(self):
        """
        Test clients are able to access their own retirement plan by id.
        """
        plan = RetirementPlanFactory.create(calculated_life_expectancy=92)
        soa = plan.statement_of_advice
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(plan.client.id, plan.id)
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client'], plan.client.id)
        self.assertEqual(response.data['calculated_life_expectancy'], plan.calculated_life_expectancy)
        self.assertNotIn('goal_setting', response.data)
        self.assertEqual(response.data['statement_of_advice'], soa.id)
        self.assertEqual(response.data['statement_of_advice_url'], '/statements/retirement/{}.pdf'.format(soa.id))
        self.assertNotEqual(response.data['created_at'], None)
        self.assertNotEqual(response.data['updated_at'], None)

    def test_agreed_on_plan_generates_soa(self):
        """
        Test agreed on retirement plan generates a statement of advice
        on save.
        """
        plan = RetirementPlanFactory.create(calculated_life_expectancy=92)
        plan.agreed_on = timezone.now()
        plan.save()

        url = '/api/v1/clients/{}/retirement-plans/{}'.format(plan.client.id, plan.id)
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client'], plan.client.id)
        self.assertEqual(response.data['calculated_life_expectancy'], plan.calculated_life_expectancy)
        self.assertNotEqual(response.data['statement_of_advice'], None)

    def test_add_plan(self):
        '''
        Tests:
        - clients can create a retirement plan.
        - specifying btc on creation works
        '''
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.post(url, self.base_plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['btc'], 3200)  # 80000 * 0.04
        self.assertNotEqual(response.data['id'], None)
        saved_plan = RetirementPlan.objects.get(id=response.data['id'])
        self.assertEqual(saved_plan.btc, 3200)

    def test_add_plan_with_json_fields(self):
        '''
        Tests:
        - clients can create a retirement plan.
        - specifying btc on creation works
        '''
        external_asset = ExternalAssetFactory.create(owner=Fixture1.client1(), valuation=100000)
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        plan_data = self.base_plan_data.copy()
        plan_data['partner_data'] = {'name': 'Freddy', 'dob': date(2000, 1, 1), 'income': 50000, 'btc': 1000}
        plan_data['expenses'] = [
            {
                "id": 1,
                "desc": "Car",
                "cat": RetirementPlan.ExpenseCategory.TRANSPORTATION.value,
                "who": "self",
                "amt": 200,
            },
        ]
        plan_data['savings'] = [
            {
                "id": 1,
                "desc": "Health Account",
                "cat": RetirementPlan.SavingCategory.HEALTH_GAP.value,
                "who": "self",
                "amt": 100,
            },
        ]
        plan_data['initial_deposits'] = [
            {
                "id": 1,
                "asset": external_asset.id,
                "amt": 10000,
            },
        ]
        response = self.client.post(url, plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['partner_data']['btc'], 1000)
        saved_plan = RetirementPlan.objects.get(id=response.data['id'])
        self.assertEqual(saved_plan.savings[0]['amt'], 100)
        self.assertEqual(saved_plan.expenses[0]['amt'], 200)
        self.assertEqual(saved_plan.initial_deposits[0]['amt'], 10000)

    def test_add_plan_no_name(self):
        base_plan_data = {
            "description": "My solo plan",
            'desired_income': 60000,
            'income': 80000,
            'volunteer_days': 1,
            'paid_days': 2,
            'btc': 1000,
            'same_home': True,
            'reverse_mortgage': True,
            'expected_return_confidence': 0.5,
        }
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.post(url, base_plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['btc'], 1000)
        self.assertNotEqual(response.data['id'], None)
        saved_plan = RetirementPlan.objects.get(id=response.data['id'])
        self.assertEqual(saved_plan.btc, 1000)
        # make sure name is None
        self.assertEqual(response.data['name'], None)

    def test_cant_change_after_agreed(self):
        '''
        Tests:
        - clients can create a retirement plan.
        - specifying btc on creation works
        '''
        client = Fixture1.client1()
        url = '/api/v1/clients/%s/retirement-plans' % client.id
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.post(url, self.base_plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Now update it with agreed_on=Now
        url = '/api/v1/clients/%s/retirement-plans/%s'%(client.id, response.data['id'])
        dt = now()
        new_data = dict(self.base_plan_data, agreed_on=dt)
        response = self.client.put(url, new_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Now we can't update it
        url = '/api/v1/clients/%s/retirement-plans/%s'%(client.id, response.data['id'])
        response = self.client.put(url, self.base_plan_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_plans(self):
        """
        Tests clients can get a list of their own plans and the list does not include plans where it is a partner.
        """
        plan1 = RetirementPlanFactory.create()
        plan2 = RetirementPlanFactory.create(partner_plan=plan1)
        url = '/api/v1/clients/{}/retirement-plans'.format(plan1.client.id)
        self.client.force_authenticate(user=plan1.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['client'], plan1.client.id)

    def test_retirement_incomes(self):
        """
        Test listing and creating retirement incomes
        """

        plan = RetirementPlanFactory.create()
        client = plan.client

        # Create an income
        url = '/api/v1/clients/%s/retirement-incomes' % client.id
        self.client.force_authenticate(user=client.user)
        income_data = {'name': 'RetirementIncome1',
                       'plan': plan.id,
                       'begin_date': now().date(),
                       'amount': 200,
                       'growth': 1.0,
                       'schedule': 'DAILY'
                       }
        response = self.client.post(url, income_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        income = response.data
        self.assertEqual(income['schedule'], 'DAILY')
        self.assertEqual(income['amount'], 200)
        self.assertEqual(income['growth'], 1.0)
        self.assertEqual(income['plan'], plan.id)

        # Update it
        url = '/api/v1/clients/%s/retirement-incomes/%s' % (client.id,
                                                            income['id'])
        income_data = { 'schedule': 'WEEKLY' }
        response = self.client.put(url, income_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Make sure it's in the list
        url = '/api/v1/clients/%s/retirement-incomes'%client.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], income['id'])

        # And unprivileged users can't see it
        self.client.force_authenticate(user=Fixture1.client2().user)
        url = '/api/v1/clients/%s/retirement-incomes'%client.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_put_partner(self):
        """
        Test update partner_plan after tax contribution
        """
        plan1 = RetirementPlanFactory.create()
        plan2 = RetirementPlanFactory.create(partner_plan=plan1)
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(plan2.client.id, plan2.id)
        self.client.force_authenticate(user=plan1.client.user)
        response = self.client.put(url, data={'atc': 45000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_plan = RetirementPlan.objects.get(id=plan2.id)
        self.assertEqual(check_plan.atc, 45000)

    def test_get_bad_permissions(self):
        """
        Test clients not owning and not on a partner plan cannot access.
        """
        plan = RetirementPlanFactory.create()
        plan2 = RetirementPlanFactory.create()
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(plan.client.id,
                                                              plan.id)
        self.client.force_authenticate(user=plan2.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {})

    def test_matching_partnerplans(self):
        """
        Test update plan (link partner plan)
        Check if partner_plan doesn't equal
        partner_plan_reverse and they both are set, then we fail.
        """
        plan1 = RetirementPlanFactory.create()
        plan2 = RetirementPlanFactory.create(partner_plan=plan1)
        plan4 = RetirementPlanFactory.create()
        plan2.reverse_partner_plan = plan4
        plan2.save()

        plan1.reverse_partner_plan = plan2
        plan1.save()

        plan3 = RetirementPlanFactory.create()

        self.assertEqual(plan1.reverse_partner_plan, plan2)
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(plan1.client.id, plan1.id)
        self.client.force_authenticate(user=plan1.client.user)
        response = self.client.put(url, data={'partner_plan': plan3.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(loads(response.content)['error']['reason'], 'ValidationError')
        self.assertEqual(response.data, {})
        # Make sure the db content didn't change
        self.assertEqual(plan2.partner_plan, plan1)

    def test_partner_delete(self):
        """
        Test on delete sets partner to null
        """
        plan1 = RetirementPlanFactory.create()
        plan2 = RetirementPlanFactory.create(partner_plan=plan1)
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(plan1.client.id, plan1.id)
        self.client.force_authenticate(user=plan1.client.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Make sure the db object was removed, and the partner plan set to null.
        self.assertEqual(RetirementPlan.objects.filter(id=plan1.id).first(), None)
        # Make sure cascade not in force, but null.
        check_plan = RetirementPlan.objects.get(id=plan2.id)
        self.assertEqual(check_plan.id, plan2.id)

        self.assertEqual(check_plan.partner_plan, None)

    def test_todos(self):
        # TODO: Advisor tests.
        # Test a clients' primary and secondary advisors are able to access the appropriate plans.
        # Test partner plan clients' primary and secondary advisors are able to access the appropriate plans.
        # Test non-advising advisors cannot access
        # Test only advisors and clients can view and edit the plans. (No-one with firm privileges)
        pass

    def test_retirement_plan_calculate_unauthenticated(self):
        plan = RetirementPlanFactory.create()
        url = '/api/v1/clients/{}/retirement-plans/{}/calculate'.format(plan.client.id, plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retirement_plan_calculate_not_found(self):
        plan = RetirementPlanFactory.create()
        url = '/api/v1/clients/{}/retirement-plans/{}/calculate'.format(plan.client.id, plan.id+999)
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch.object(timezone, 'now', MagicMock(return_value=mocked_now))
    def test_retirement_plan_calculate(self):
        plan = RetirementPlanFactory.create(income=100000,
                                            desired_income=81000,
                                            btc=4000,
                                            retirement_home_price=250000,
                                            paid_days=1,
                                            retirement_age=67,
                                            selected_life_expectancy=85)

        # some tickers for portfolio
        bonds_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.BONDS.get())
        stocks_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.STOCKS.get())
        bonds_index = MarketIndexFactory.create()
        stocks_index = MarketIndexFactory.create()

        # Add the asset classes to the advisor's default portfolio set
        plan.client.advisor.default_portfolio_set.asset_classes.add(bonds_asset_class, stocks_asset_class)
        bonds_ticker = TickerFactory.create(asset_class=bonds_asset_class, benchmark=bonds_index)
        stocks_ticker = TickerFactory.create(asset_class=stocks_asset_class, benchmark=stocks_index)

        # Set the markowitz bounds for today
        self.m_scale = MarkowitzScaleFactory.create()

        # populate the data needed for the optimisation
        # We need at least 500 days as the cycles go up to 70 days and we need at least 7 cycles.
        populate_prices(500, asof=mocked_now.date())
        populate_cycle_obs(500, asof=mocked_now.date())
        populate_cycle_prediction(asof=mocked_now.date())
        populate_inflation(asof=mocked_now.date())

        self.assertIsNone(plan.goal_setting)
        old_settings = GoalSetting.objects.all().count()
        old_mgroups = GoalMetricGroup.objects.all().count()
        old_metrics = GoalMetric.objects.all().count()
        url = '/api/v1/clients/{}/retirement-plans/{}/calculate'.format(plan.client.id, plan.id)
        self.client.force_authenticate(user=plan.client.user)

        # First try and calculate without a client date of birth. Make sure we get the correct 400
        old_dob = plan.client.date_of_birth
        plan.client.date_of_birth = None
        plan.client.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Now set the date of birth
        plan.client.date_of_birth = old_dob
        plan.client.save()

        # We should be ready to calculate properly
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('portfolio' in response.data)
        self.assertTrue('projection' in response.data)
        self.assertEqual(len(response.data['projection']), 50)
        # Make sure the goal_setting is now populated.
        plan.refresh_from_db()
        self.assertIsNotNone(plan.goal_setting.portfolio)
        self.assertEqual(old_settings+1, GoalSetting.objects.all().count())
        self.assertEqual(old_mgroups+1, GoalMetricGroup.objects.all().count())
        self.assertEqual(old_metrics+1, GoalMetric.objects.all().count())
        old_id = plan.goal_setting.id

        # Recalculate and make sure the number of settings, metric groups and metrics in the system is the same
        # Also make sure the setting object is different
        response = self.client.get(url)
        plan.refresh_from_db()
        self.assertEqual(old_settings+1, GoalSetting.objects.all().count())
        self.assertEqual(old_mgroups+1, GoalMetricGroup.objects.all().count())
        self.assertEqual(old_metrics+1, GoalMetric.objects.all().count())
        self.assertNotEqual(old_id, plan.goal_setting.id)

    def test_retirement_plan_advice_feed_list_unread(self):
        self.content_type = ContentTypeFactory.create()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.BONDS.get())
        self.stocks_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.STOCKS.get())
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark_content_type=self.content_type)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark_content_type=self.content_type)
        plan = RetirementPlanFactory.create()
        elog = log(user=plan.client.user, action='Triggers retirement advice')
        advice = RetirementAdviceFactory(plan=plan, trigger=elog, read=timezone.now())
        elog2 = log(user=plan.client.user, action='Triggers another, unread retirement advice')
        advice2 = RetirementAdviceFactory(plan=plan, trigger=elog)
        url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed'.format(plan.client.id, plan.id)
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('results')[0]['id'], advice.id)
        self.assertEqual(response.data.get('results')[0]['id'], advice2.id)
        self.assertEqual(response.data.get('count'), 1)

    def test_retirement_plan_advice_feed_detail(self):
        self.content_type = ContentTypeFactory.create()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.BONDS.get())
        self.stocks_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.STOCKS.get())
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark_content_type=self.content_type)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark_content_type=self.content_type)
        plan = RetirementPlanFactory.create()
        elog = log(user=plan.client.user, action='Triggers retirement advice')
        advice = RetirementAdviceFactory(plan=plan, trigger=elog)
        url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed/{}'.format(plan.client.id, plan.id, advice.id)
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], advice.id)

    def test_retirement_plan_advice_fed_update(self):
        self.content_type = ContentTypeFactory.create()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.BONDS.get())
        self.stocks_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.STOCKS.get())
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark_content_type=self.content_type)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark_content_type=self.content_type)
        plan = RetirementPlanFactory.create()
        elog = log(user=plan.client.user, action='Triggers retirement advice')
        advice = RetirementAdviceFactory(plan=plan, trigger=elog)
        url = '/api/v1/clients/{}/retirement-plans/{}/advice-feed/{}'.format(plan.client.id, plan.id, advice.id)
        self.client.force_authenticate(user=plan.client.user)
        read_time = timezone.now()
        data = {
            'read': read_time,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], advice.id)
        self.assertEqual(response.data['read'][:9], str(read_time)[:9])

    def test_add_retirement_plan_same_location_no_postal(self):
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        data = {
            "name": "Personal Plan",
            "description": "My solo plan",
            'desired_income': 60000,
            'income': 80000,
            'volunteer_days': 1,
            'paid_days': 2,
            'same_home': False,
            'same_location': True,
            'reverse_mortgage': True,
            'expected_return_confidence': 0.5,
            'retirement_age': 65,
            'btc': 1000,
            'atc': 300,
            'desired_risk': 0.6,
            'selected_life_expectancy': 80,
        }
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['btc'], 1000)
        self.assertNotEqual(response.data['id'], None)
        saved_plan = RetirementPlan.objects.get(id=response.data['id'])
        self.assertEqual(saved_plan.btc, 1000)
        self.assertEqual(saved_plan.retirement_age, 65)

    def test_add_retirement_plan_with_savings(self):
        savings = [{
            "cat": 3,
            "amt": 10000,
            "desc": "123",
            "who": "self",
            "id": 1
        }]
        self.base_plan_data['savings'] = savings
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.post(url, self.base_plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['btc'], 3200)  # 80000 * 0.04
        self.assertNotEqual(response.data['id'], None)
        saved_plan = RetirementPlan.objects.get(id=response.data['id'])
        self.assertEqual(saved_plan.btc, 3200)
        self.assertNotEqual(response.data['savings'], None)
        self.assertEqual(response.data['savings'][0]['id'], 1)
        self.assertEqual(response.data['savings'][0]['amt'], 10000)

    def test_add_retirement_plan_with_expenses(self):
        expenses = [{
            "cat": 3,
            "amt": 10000,
            "desc": "123",
            "who": "self",
            "id": 1
        }]
        self.base_plan_data['expenses'] = expenses
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.post(url, self.base_plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['btc'], 3200)  # 80000 * 0.04
        self.assertNotEqual(response.data['id'], None)
        saved_plan = RetirementPlan.objects.get(id=response.data['id'])
        self.assertEqual(saved_plan.btc, 3200)
        self.assertNotEqual(response.data['expenses'], None)
        self.assertEqual(response.data['expenses'][0]['id'], 1)
        self.assertEqual(response.data['expenses'][0]['amt'], 10000)
