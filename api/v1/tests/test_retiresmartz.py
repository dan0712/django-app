from ujson import loads
from unittest import skip

from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APITestCase

from common.constants import GROUP_SUPPORT_STAFF
from main.models import RetirementPlan
from main.tests.fixture import Fixture1
from .factories import GroupFactory


class RetiresmartzTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)

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

    @skip("Broken")
    def test_add_plan(self):
        '''
        Tests:
        - clients can create a retirement plan.
        - specifying btc on creation works
        '''
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        plan_data = {
            "name": "Personal Plan",
            "description": "My solo plan",
            "btc": {
                'begin_date': now().today(),
                'amount': 1000,
                'growth': 0.025,
                'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1',
            },
            "external_income": [{
                'begin_date': now().today(),
                'amount': 2000,
                'growth': 0.01,
                'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1',
            }],
        }
        response = self.client.post(url, plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['btc']['amount'], 1000)
        saved_plan = RetirementPlan.objects.get(id=response.data['id'])
        self.assertEqual(saved_plan.btc.amount, 1000)
        self.assertEqual(saved_plan.external_income.count(), 1)
        self.assertEqual(saved_plan.external_income.first().amount, 2000)

    @skip("Broken")
    def test_add_plan_smsf_account_ignored(self):
        '''
        Tests:
        - clients cannot create a retirement plan assigning an smsf account.
        '''
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        plan_data = {
            "name": "Personal Plan",
            "description": "My solo plan",
            "smsf_account": 1,
        }
        response = self.client.post(url, plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RetirementPlan.objects.get(id=response.data['id']).smsf_account, None)

    @skip("Broken")
    def test_add_plan_id_ignored(self):
        '''
        Tests clients cannot create a retirement plan and specify the id manually.
        '''
        url = '/api/v1/clients/{}/retirement-plans'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        plan_data = {
            "name": "Personal Plan",
            "description": "My solo plan",
            "id": 756,
        }
        response = self.client.post(url, plan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['id'], 756)

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

    def test_put_partner(self):
        """
        Test update partner_plan after tax contribution
        """
        plan1 = Fixture1.client1_partneredplan()
        Fixture1.retirement_plan_atc3()
        plan2 = plan1.partner_plan
        url = '/api/v1/clients/{}/retirement-plans/{}'.format(Fixture1.client2().id, plan2.id)
        self.client.force_authenticate(user=Fixture1.client1().user)
        response = self.client.put(url, data={'atc': {
            'begin_date': plan2.atc.begin_date,
            'amount': 7654,
            'growth': plan2.atc.growth,
            'schedule': plan2.atc.schedule,
        }})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Fixture1.client2_retirementplan1().atc.amount, 7654)

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
