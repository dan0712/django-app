from ujson import loads

from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import GROUP_SUPPORT_STAFF
from main.models import InvestmentType
from main.tests.fixture import Fixture1
from retiresmartz.models import RetirementPlan
from .factories import AssetClassFactory, ContentTypeFactory, GroupFactory, \
    RetirementPlanFactory, TickerFactory, RetirementAdviceFactory
from django.utils import timezone
from pinax.eventlog.models import log


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
        }

    def tearDown(self):
        self.client.logout()

    def test_get_plan(self):
        """
        Test clients are able to access their own retirement plan by id.
        """
        plan1 = Fixture1.client1_retirementplan1()
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(Fixture1.client1().id, plan1.id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client'], plan1.client.id)
        self.assertEqual(response.data['calculated_life_expectancy'], 85)

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
        plan1 = Fixture1.client1_partneredplan()
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['client'], plan1.client.id)

    def test_retirement_incomes(self):
        """
        Test listing and creating retirement incomes
        """
        client = Fixture1.client1()
        plan = Fixture1.client1_retirementplan1()

        # Create an income
        url = '/api/v1/clients/%s/retirement-incomes'%client.id
        self.client.force_authenticate(user=Fixture1.client1().user)
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
        url = '/api/v1/clients/%s/retirement-incomes/%s'%(client.id,
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
        plan1 = Fixture1.client1_partneredplan()
        plan2 = plan1.partner_plan
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(Fixture1.client2().id, plan2.id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.put(url, data={'atc': 45000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Fixture1.client2_retirementplan1().atc, 45000)

    def test_get_bad_permissions(self):
        """
        Test clients not owning and not on a partner plan cannot access.
        """
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(Fixture1.client2().id,
                                                              Fixture1.client2_retirementplan1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {})

    def test_matching_partnerplans(self):
        """
        Test update plan (link partner plan)
        Check if partner_plan doesn't equal partner_plan_reverse and they both are set, then we fail.
        """
        plan1 = Fixture1.client1_partneredplan()
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(Fixture1.client1().id, plan1.id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.put(url, data={'partner_plan': Fixture1.client2_retirementplan2().id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(loads(response.content)['error']['reason'], 'ValidationError')
        self.assertEqual(response.data, {})
        # Make sure the db content didn't change
        self.assertEqual(Fixture1.client1_retirementplan1().partner_plan, Fixture1.client2_retirementplan1())

    def test_partner_delete(self):
        """
        Test on delete sets partner to null
        """
        plan1 = Fixture1.client1_partneredplan()
        plan1_id = plan1.id
        plan2_id = plan1.partner_plan.id
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(Fixture1.client1().id, plan1_id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Make sure the db object was removed, and the partner plan set to null.
        self.assertEqual(RetirementPlan.objects.filter(id=plan1_id).first(), None)
        # Make sure cascade not in force, but null.
        self.assertEqual(RetirementPlan.objects.get(id=plan2_id).id, plan2_id)
        self.assertEqual(Fixture1.client2_retirementplan1().partner_plan, None)

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

    def test_retirement_plan_calculate(self):
        # some tickers for portfolio
        self.content_type = ContentTypeFactory.create()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.BONDS.get())
        self.stocks_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.STOCKS.get())
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark_content_type=self.content_type)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark_content_type=self.content_type)
        plan = RetirementPlanFactory.create()
        url = '/api/v1/clients/{}/retirement-plans/{}/calculate'.format(plan.client.id, plan.id)
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('portfolio' in response.data)
        self.assertTrue('projection' in response.data)

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

    def test_retirement_plan_calculate_income(self):
        self.content_type = ContentTypeFactory.create()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.BONDS.get())
        self.stocks_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.STOCKS.get())
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark_content_type=self.content_type)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark_content_type=self.content_type)
        plan = RetirementPlanFactory.create()
        url = '/api/v1/clients/{}/retirement-plans/{}/calculate-income'.format(plan.client.id, plan.id)
        self.client.force_authenticate(user=plan.client.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
