# -*- coding: utf-8 -*-
from django.test import TestCase
from django.views.generic import TemplateView
from main.views.firm.dashboard import FirmAnalyticsMixin
from main import constants
from main.models import Transaction, Goal
from django.db.models import Q
from api.v1.tests.factories import ClientAccountFactory, \
    ClientFactory, GoalFactory, \
    TransactionFactory, AccountTypeRiskProfileGroupFactory, \
    ExternalAssetFactory
from client.models import Client
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class FirmAnalyticsMixinTests(TestCase):
    class DummyView(FirmAnalyticsMixin, TemplateView):
        template_name = 'firm/analytics.html'

    def setUp(self):
        super(FirmAnalyticsMixinTests, self).setUp()
        self.view = self.DummyView()
        # Populate the AccountType -> RiskProfileGroup mapping
        for atid, _ in constants.ACCOUNT_TYPES:
            AccountTypeRiskProfileGroupFactory.create(account_type=atid)
        # first client
        self.betasmartz_client = ClientFactory.create()
        self.client_account = ClientAccountFactory.create(primary_owner=self.betasmartz_client, account_type=constants.ACCOUNT_TYPE_PERSONAL)
        self.firm = self.betasmartz_client.advisor.firm

        self.external_asset1 = ExternalAssetFactory.create(owner=self.betasmartz_client)
        self.external_asset2 = ExternalAssetFactory.create(owner=self.betasmartz_client)
        self.goal = GoalFactory.create(account=self.client_account)
        self.goal2 = GoalFactory.create(account=self.client_account)
        self.transaction = TransactionFactory.create(to_goal=self.goal,
                                                     from_goal=self.goal2,
                                                     amount=self.goal.cash_balance,
                                                     status=Transaction.STATUS_EXECUTED,
                                                     reason=Transaction.REASON_TRANSFER,
                                                     executed=date.today())

        # second client
        self.betasmartz_client2 = ClientFactory.create(advisor=self.betasmartz_client.advisor)
        self.client_account2 = ClientAccountFactory.create(primary_owner=self.betasmartz_client2, account_type=constants.ACCOUNT_TYPE_PERSONAL)
        self.external_asset1 = ExternalAssetFactory.create(owner=self.betasmartz_client2)
        self.external_asset2 = ExternalAssetFactory.create(owner=self.betasmartz_client2)

        self.goal3 = GoalFactory.create(account=self.client_account2)
        self.goal4 = GoalFactory.create(account=self.client_account2)
        self.transaction2 = TransactionFactory.create(to_goal=self.goal3,
                                                      from_goal=self.goal4,
                                                      amount=self.goal3.cash_balance,
                                                      status=Transaction.STATUS_EXECUTED,
                                                      reason=Transaction.REASON_TRANSFER,
                                                      executed=date.today())

    def tearDown(self):
        pass

    def test_get_context_worth(self):
        """
        expecting context to return a list of dictionaries

        [
            {
                'value_worth': average client net worth,
                'value_cashflow': average client cashflow,
                'age': clients of this age,
            },
            ...
        ]

        This test is to validate the value_cashflow and value_worth both match
        expected values.
        """
        kwargs = {}

        def average_net_worths(firm):
            rt = []
            current_date = datetime.now().today()
            for age in self.view.AGE_RANGE:
                average_net_worth = 0.0
                range_dates = map(lambda x: current_date - relativedelta(years=x),
                                  [age + self.view.AGE_STEP, age])

                # gather clients of firm of this age
                firm_clients = Client.objects.filter(advisor__firm=firm)
                # print(firm_clients.first())
                clients_by_age = firm_clients.filter(date_of_birth__range=range_dates)
                # sum client.net_worth and divide by number of clients
                for client in clients_by_age:
                    average_net_worth += client.net_worth
                if clients_by_age.count() > 0:
                    average_net_worth = average_net_worth / clients_by_age.count()
                rt.append(average_net_worth)
            return rt

        def average_cashflows(firm):
            rt = []
            current_date = datetime.now().today()
            for age in self.view.AGE_RANGE:
                total_cashflow = 0.0
                average_client_cashflow = 0.0
                range_dates = map(lambda x: current_date - relativedelta(years=x),
                                  [age + self.view.AGE_STEP, age])

                # get goals for firm
                qs_goals = Goal.objects.all().filter_by_firm(firm)
                cashflow_goals = qs_goals.filter_by_client_age(age, age + self.view.AGE_STEP)
                number_of_clients = 0
                number_of_clients += len(set([goal.account.primary_owner for goal in cashflow_goals]))
                for goal in cashflow_goals:
                    txs = Transaction.objects.filter(Q(to_goal=goal) | Q(from_goal=goal),
                                                     status=Transaction.STATUS_EXECUTED,
                                                     reason__in=Transaction.CASH_FLOW_REASONS) \
                                                    .filter(executed__gt=date.today() - relativedelta(years=1)) \
                                                    .filter(executed__gt=date.today() - relativedelta(years=1))
                    
                    # subtract from_goal amounts and add to_goal amounts
                    for tx in txs:
                        if tx.from_goal:
                            total_cashflow -= tx.amount
                        elif tx.to_goal:
                            total_cashflow += tx.amount

                # divide total cashflow by number of clients
                if number_of_clients > 0:
                    average_client_cashflow = total_cashflow / number_of_clients
                rt.append(average_client_cashflow)
            return rt

        context = self.view.get_context_worth(**kwargs)
        test_worths = []
        expected_worths = average_net_worths(self.firm)
        test_cashflows = []
        expected_cashflows = average_cashflows(self.firm)
        for d in context:
            test_worths.append(d['value_worth'])
            test_cashflows.append(d['value_cashflow'])
        # print(expected_worths, test_worths)
        self.assertEqual(expected_worths, test_worths)
        # print(expected_cashflows, test_cashflows)
        self.assertEqual(expected_cashflows, test_cashflows)