from rest_framework import status
from rest_framework.test import APITestCase

from main.models import ExternalAsset
from main.tests.fixtures import Fixture1
from .factories import ClientFactory, ClientAccountFactory, ExternalAssetFactory, \
                       RegionFactory, AddressFactory, RiskProfileGroupFactory, AccountTypeRiskProfileGroupFactory, \
                       GroupFactory
from main.constants import ACCOUNT_TYPE_PERSONAL
from common.constants import GROUP_SUPPORT_STAFF


class ClientTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        # client with some personal assets, cash balance and goals
        self.region = RegionFactory.create()
        self.betasmartz_client_address = AddressFactory(region=self.region)
        self.risk_group = RiskProfileGroupFactory.create(name='Personal Risk Profile Group')
        self.personal_account_type = AccountTypeRiskProfileGroupFactory.create(account_type=0,
                                                                               risk_profile_group=self.risk_group)
        self.betasmartz_client = ClientFactory.create()

        self.betasmartz_client_account = ClientAccountFactory(primary_owner=self.betasmartz_client, account_type=ACCOUNT_TYPE_PERSONAL)
        self.external_asset1 = ExternalAssetFactory.create(owner=self.betasmartz_client)
        self.external_asset2 = ExternalAssetFactory.create(owner=self.betasmartz_client)

    def tearDown(self):
        self.client.logout()

    def test_create_external_asset(self):
        url = '/api/v1/clients/{}/external-assets'.format(Fixture1.client1().id)
        old_count = ExternalAsset.objects.count()
        self.client.force_authenticate(user=Fixture1.client1_user())

        # First input details about the loan.
        loan_data = {
            'type': ExternalAsset.Type.PROPERTY_LOAN.value,
            'name': 'My Home Loan',
            'owner': Fixture1.client1().id,
            # description intentionally omitted to test optionality
            'valuation': -145000,
            'valuation_date': '2016-07-05',
            'growth': 0.03,
            'transfer_plan': {
                'begin_date': '2016-07-05',
                'amount': 1000,
                'growth': 0.0,
                'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
            },
            'acquisition_date': '2016-07-03',
        }
        response = self.client.post(url, loan_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure the object was returned correctly
        self.assertTrue('id' in response.data)
        self.assertEqual(response.data['name'], 'My Home Loan')

        # Make sure the object was added to the DB, along with it's transfer plan
        self.assertEqual(ExternalAsset.objects.count(), old_count + 1)
        debt = ExternalAsset.objects.get(id=response.data['id'])
        self.assertEqual(debt.name, 'My Home Loan')
        self.assertEqual(debt.transfer_plan.amount, 1000)

        # Now submit details about the asset
        data = {
            'type': ExternalAsset.Type.FAMILY_HOME.value,
            'name': 'My Home',
            'owner': Fixture1.client1().id,
            'description': 'This is my beautiful home',
            'valuation': 345000.01,
            'valuation_date': '2016-07-05',
            'growth': 0.01,
            # trasfer_plan intentionally omitted as there isn't one
            'acquisition_date': '2016-07-03',
            'debt': debt.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure the object was added to the DB
        self.assertEqual(ExternalAsset.objects.count(), old_count + 2)
        house = ExternalAsset.objects.get(id=response.data['id'])
        self.assertEqual(house.name, 'My Home')

    def test_update_asset(self):
        asset = Fixture1.external_asset_1()
        url = '/api/v1/clients/{}/external-assets/{}'.format(Fixture1.client1().id, asset.id)
        test_name = 'Holy Pingalicious Test Asset'
        self.assertNotEqual(asset.name, test_name)
        data = {
            'name': test_name,
        }
        old_count = ExternalAsset.objects.count()
        self.client.force_authenticate(user=Fixture1.client1_user())
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExternalAsset.objects.count(), old_count)  # No extra asset created
        self.assertTrue('id' in response.data)  # Correct response serializer used
        self.assertEqual(response.data['name'], test_name)  # New value returned
        asset.refresh_from_db()
        self.assertEqual(asset.name, test_name)  # Value in db actually changed

    def test_update_asset_no_id(self):
        """
        Make sure we can't update or set the id.
        """
        self.client.force_authenticate(user=Fixture1.client1_user())

        # Try for update
        asset = Fixture1.external_asset_1()
        self.assertNotEqual(asset.id, 999)
        url = '/api/v1/clients/{}/external-assets/{}'.format(Fixture1.client1().id, asset.id)
        data = {'id': 999}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], asset.id)

        # Try for create
        url = '/api/v1/clients/{}/external-assets'.format(Fixture1.client1().id)
        data = {
            'id': 999,
            'type': ExternalAsset.Type.FAMILY_HOME.value,
            'name': 'My Home 2',
            'owner': Fixture1.client1().id,
            'description': 'This is my beautiful home',
            'valuation': 345000.01,
            'valuation_date': '2016-07-05',
            'growth': 0.01,
            # trasfer_plan intentionally omitted as there isn't one
            'acquisition_date': '2016-07-03'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['id'], 999)

    def test_get_all_assets(self):
        url = '/api/v1/clients/{}/external-assets'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client1_user())

        # First check when there are none, we get the appropriate response
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

        # Then add one and make sure it is returned
        asset = Fixture1.external_asset_1()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # One for the asset, and 1 for the associated debt.
        self.assertEqual(response.data[0]['name'], asset.debt.name)
        self.assertEqual(response.data[1]['name'], asset.name)

    def test_get_asset_detail(self):
        url = '/api/v1/clients/{}/external-assets/{}'.format(Fixture1.client1().id, Fixture1.external_asset_1().id)
        self.client.force_authenticate(user=Fixture1.client1_user())
        asset = Fixture1.external_asset_1()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], asset.type)
        self.assertEqual(response.data['name'], asset.name)
        self.assertFalse('owner' in response.data)
        self.assertEqual(response.data['description'], asset.description)
        self.assertEqual(response.data['valuation'], asset.valuation)
        self.assertEqual(response.data['valuation_date'], '2016-07-05')
        self.assertEqual(response.data['acquisition_date'], '2016-07-03')
        self.assertEqual(response.data['growth'], asset.growth)
        self.assertEqual(response.data['debt'], asset.debt.id)

    def test_delete_asset(self):
        asset1 = Fixture1.external_asset_1()
        url = '/api/v1/clients/{}/external-assets/{}'.format(Fixture1.client1().id, asset1.id)
        self.client.force_authenticate(user=Fixture1.client1_user())

        old_count = ExternalAsset.objects.count()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) # Correct code received
        self.assertEqual(response.data, None) # Nothing returned

        # Check Item no longer in DB
        self.assertEqual(ExternalAsset.objects.count(), old_count - 1)  # Asset removed
        self.assertIsNone(ExternalAsset.objects.filter(id=asset1.id).first())

    def test_access(self):
        """
        test that users cannot see assets they are not authorised to
        :return:
        """
        asset1 = Fixture1.external_asset_1()
        url = '/api/v1/clients/{}/external-assets'.format(Fixture1.client1().id)
        self.client.force_authenticate(user=Fixture1.client2_user())
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Correct code received
        self.assertEqual(response.data, [])  # No assets available.

        # Now change to the authorised user, and we should get stuff.
        self.client.force_authenticate(user=Fixture1.client1_user())
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Correct code received
        self.assertEqual(len(response.data), 2)  # Assets available.

    # Tests below this validate the client model's internal functionality
    # they do not test api endpoints
    def test_net_worth(self):
        """
        verify that the client's net worth property returns the expected
        amount for the client's assets
        """
        # # expected net_worth here - ?
        # expected_net_worth = 0.0
        # total external assets valuation
        assets_sum = self.external_asset1.valuation + self.external_asset2.valuation
        # accounts_sum = 
        # self.assertTrue(client.net_worth == expected_net_worth)
        pass
