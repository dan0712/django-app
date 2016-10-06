from django.test import TestCase

from api.v1.tests.factories import ClientFactory, ClientAccountFactory, ExternalAssetFactory, \
                                   RegionFactory, AddressFactory, RiskProfileGroupFactory, \
                                   AccountTypeRiskProfileGroupFactory, GroupFactory, UserFactory, \
                                   GoalFactory, StatementOfAdviceFactory
from main.constants import ACCOUNT_TYPE_PERSONAL
from common.constants import GROUP_SUPPORT_STAFF

import sys


class StatementTest(TestCase):
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
    def test_statement_pdf(self):
        TEST_TEMPLATE = "statements/_test_soa.html"
        soa = StatementOfAdviceFactory(account=self.betasmartz_client_account)

        html = soa.render_template(TEST_TEMPLATE)
        # Make sure we have the basic stuff
        self.assertIn(self.betasmartz_client.full_name, html)
        self.assertIn(self.betasmartz_client.advisor.name, html)
        self.assertIn(self.betasmartz_client.firm.colored_logo.replace('&', '&amp;'), html)

        test_pdf = soa.render_pdf(TEST_TEMPLATE)
        real_soa = soa.render_pdf()

        self.assertGreaterEqual(len(test_pdf), 25*1024)
        self.assertGreaterEqual(len(real_soa), 25*1024)

        if '-v3' in sys.argv:
            open('.test.blank-soa.pdf', 'wb+').write(test_pdf)
            open('.test.real-soa.pdf', 'wb+').write(real_soa)
