from django.test import TestCase

from api.v1.tests.factories import ClientFactory, ClientAccountFactory, ExternalAssetFactory, \
                                   RegionFactory, AddressFactory, RiskProfileGroupFactory, \
                                   AccountTypeRiskProfileGroupFactory, GroupFactory, UserFactory, \
                                   GoalFactory
from main.constants import ACCOUNT_TYPE_PERSONAL
from common.constants import GROUP_SUPPORT_STAFF


class ClientTests(TestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        # client with some personal assets, cash balance and goals
        self.region = RegionFactory.create()
        self.betasmartz_client_address = AddressFactory(region=self.region)
        self.risk_group = RiskProfileGroupFactory.create(name='Personal Risk Profile Group')
        self.personal_account_type = AccountTypeRiskProfileGroupFactory.create(account_type=0,
                                                                               risk_profile_group=self.risk_group)
        self.user = UserFactory.create()
        self.betasmartz_client = ClientFactory.create(user=self.user)

        self.betasmartz_client_account = ClientAccountFactory(primary_owner=self.betasmartz_client, account_type=ACCOUNT_TYPE_PERSONAL)
        self.external_asset1 = ExternalAssetFactory.create(owner=self.betasmartz_client)
        self.external_asset2 = ExternalAssetFactory.create(owner=self.betasmartz_client)

        self.goal1 = GoalFactory.create(account=self.betasmartz_client_account)
        self.goal2 = GoalFactory.create(account=self.betasmartz_client_account)

        self.betasmartz_client2 = ClientFactory.create()

    def tearDown(self):
        self.client.logout()

    # Tests below this validate the client model's internal functionality
    # they do not test api endpoints
    def test_net_worth(self):
        """
        verify that the client's net worth property returns the expected
        amount for the client's assets
        """
        # total external assets valuation)
        assets_sum = self.external_asset1.get_growth_valuation() + self.external_asset2.get_growth_valuation()
        # a clientaccount with a cash balance and some goals
        accounts_sum = 0.0
        accounts_sum += self.betasmartz_client_account.cash_balance
        for goal in self.betasmartz_client_account.goals:
            accounts_sum += goal.cash_balance
        expected_net_worth = float(assets_sum) + accounts_sum
        # print(self.betasmartz_client._net_worth(), expected_net_worth)
        self.assertTrue(round(self.betasmartz_client.net_worth, 10) == round(expected_net_worth, 10))

        # expecting client.net_worth using @property to have cached this initial result
        # lets make sure the underlying client._net_worth() function is tracking the right info
        # ok, let's add to the cash balance and check again
        self.betasmartz_client_account.cash_balance += 2000.0
        self.betasmartz_client_account.save()
        expected_net_worth += 2000.0
        # print(self.betasmartz_client._net_worth(), expected_net_worth)
        self.assertTrue(round(self.betasmartz_client._net_worth(), 10) == round(expected_net_worth, 10))
