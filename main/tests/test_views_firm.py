# -*- coding: utf-8 -*-
from django.test import TestCase
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from main.views.firm.dashboard import FirmAnalyticsMixin
from main import constants
from main.models import Transaction, Goal, GoalType, MarketOrderRequest, Execution, ExecutionDistribution
from main.models import Transaction, Goal, GoalType, InvestmentType
from django.db.models import Q
from api.v1.tests.factories import ClientAccountFactory, \
    ClientFactory, GoalFactory, \
    TransactionFactory, AccountTypeRiskProfileGroupFactory, \
    ExternalAssetFactory, TickerFactory, \
    SupervisorFactory, AuthorisedRepresentativeFactory, \
    InvestmentTypeFactory, PositionLotFactory, \
    ExternalAssetFactory, TickerFactory, \
    GroupFactory
from client.models import Client
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import status
from common.constants import GROUP_SUPPORT_STAFF


class FirmAnalyticsMixinTests(TestCase):
    class DummyView(FirmAnalyticsMixin, TemplateView):
        template_name = 'firm/analytics.html'

    def setUp(self):
        super(FirmAnalyticsMixinTests, self).setUp()
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.bonds_type = InvestmentType.Standard.BONDS.get()
        self.stocks_type = InvestmentType.Standard.STOCKS.get()

        self.view = self.DummyView()
        self.today = today = timezone.now().date()
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
                                                     executed=self.today)

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
                                                      executed=self.today)

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
                                                    .filter(executed__gt=self.today - relativedelta(years=1))

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
        self.assertEqual(expected_worths, test_worths)
        self.assertEqual(expected_cashflows, test_cashflows)

    def test_get_context_positions(self):
        kwargs = {}
        # empty queries tests, should be empty unless Positions are
        # added to setUp

        positions = self.view.get_context_positions(**kwargs)
        self.assertSequenceEqual(positions.get('asset_class'), [])
        self.assertSequenceEqual(positions.get('region'), [])
        self.assertSequenceEqual(positions.get('investment_type'), [])

        # now we're going to add some data and rerun sequence tests
        # have to specify content_type here because ticker uses the django
        # built in contenttype it causes problems here otherwise,
        # TODO: maybe some more elegant factoryboy solution here?
        ticker1 = TickerFactory.create()
        ticker2 = TickerFactory.create(benchmark_content_type=ticker1.benchmark_content_type)
        ticker3 = TickerFactory.create(benchmark_content_type=ticker1.benchmark_content_type)

        goal = GoalFactory.create()
        today = date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        order = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec1 = Execution.objects.create(asset=ticker1,
                                         volume=10,
                                         order=order,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=20)
        t1 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=20)
        dist1 = ExecutionDistribution.objects.create(execution=exec1, transaction=t1, volume=10)
        position1 = PositionLotFactory(quantity=10, execution_distribution=dist1)

        exec2 = Execution.objects.create(asset=ticker2,
                                         volume=10,
                                         order=order,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=20)
        t2 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=20)
        dist2 = ExecutionDistribution.objects.create(execution=exec2, transaction=t2, volume=10)
        position2 = PositionLotFactory(quantity=10, execution_distribution=dist2)

        exec3 = Execution.objects.create(asset=ticker3,
                                         volume=10,
                                         order=order,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=20)
        t3 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=20)
        dist3 = ExecutionDistribution.objects.create(execution=exec3, transaction=t3, volume=10)
        position3 = PositionLotFactory(quantity=10, execution_distribution=dist3)

        positions = self.view.get_context_positions(**kwargs)

        # should be three results, one for each position we just added
        self.assertEqual(len(positions.get('asset_class')), 3)
        self.assertEqual(len(positions.get('region')), 3)
        self.assertEqual(len(positions.get('investment_type')), 3)

        # compare sum of values to double check values being passed
        expected_sum = position1.quantity * ticker1.unit_price + \
                       position2.quantity * ticker2.unit_price + \
                       position3.quantity * ticker3.unit_price

        asset_actual_sum = sum([x.get('value') for x in positions.get('asset_class')])
        region_actual_sum = sum([x.get('value') for x in positions.get('region')])
        investment_actual_sum = sum([x.get('value') for x in positions.get('investment_type')])
        self.assertAlmostEqual(expected_sum, asset_actual_sum)
        self.assertAlmostEqual(expected_sum, region_actual_sum)
        self.assertAlmostEqual(expected_sum, investment_actual_sum)

    def test_get_context_events(self):
        kwargs = {}
        context = self.view.get_context_events(**kwargs)

        # these should be 4 goals here from setup
        original_context_len = len(context)
        # check number of goals passed matches
        self.assertEqual(original_context_len, 4)

        # check categories
        expected_categories = [gt.name for gt in GoalType.objects.all()]
        actual_categories = [x.get('category') for x in context]
        for category in expected_categories:
            self.assertTrue(category in actual_categories)

        # now lets add some more data and verify it is added
        goal1 = GoalFactory.create()
        goal2 = GoalFactory.create()
        goal3 = GoalFactory.create()

        context = self.view.get_context_events(**kwargs)
        # check number of goals passed matches
        self.assertEqual(original_context_len + 3, len(context))
        # check categories
        expected_categories = [gt.name for gt in GoalType.objects.all()]
        actual_categories = [x.get('category') for x in context]
        for category in expected_categories:
            self.assertTrue(category in actual_categories)

    def test_get_firm_analytics(self):
        """
        Test get request to firm analytics page
        """
        url = reverse('firm:analytics')
        rep = AuthorisedRepresentativeFactory.create()
        self.client.login(username=rep.user.email, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_firm_analytics_risk_filter(self):
        """
          Test get request to firm analytics with risk filter
        """
        url = reverse('firm:analytics') + '?advisor=&client=&worth=&risk=40'
        rep = AuthorisedRepresentativeFactory.create()
        self.client.login(username=rep.user.email, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_firm_analytics_worth_filter(self):
        """
          Test get request to firm analytics with risk filter
        """
        url = reverse('firm:analytics') + '?client=' + self.betasmartz_client.email + '&worth=&risk=40'
        rep = AuthorisedRepresentativeFactory.create()
        self.client.login(username=rep.user.email, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_firm_analytics_client_filter(self):
        """
          Test get request to firm analytics with risk filter
        """
        url = reverse('firm:analytics') + '?worth=high&advisor=&client='
        rep = AuthorisedRepresentativeFactory.create()
        self.client.login(username=rep.user.email, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
