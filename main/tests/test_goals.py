from datetime import datetime, timedelta, date
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from api.v1.tests.factories import TickerFactory, GoalFactory, TransactionFactory, ExecutionDistributionFactory, \
    PositionLotFactory, ContentTypeFactory, AssetClassFactory
from main.models import Goal, Transaction, MarketOrderRequest, Execution, InvestmentType
from main.tests.fixture import Fixture1


class CreateGoalTest(TestCase):
    def test_account_must_be_confirmed(self):
        account = Fixture1.personal_account1()
        account.confirmed = False
        account.save()
        self.assertFalse(account.confirmed)

        with self.assertRaises(ValidationError) as e:
            goal = Goal.objects.create(account=Fixture1.personal_account1(),
                                       name='goal1',
                                       type=Fixture1.goal_type1(),
                                       portfolio_set=Fixture1.portfolioset1(),
                                       selected_settings=Fixture1.settings1())


class GoalTests(TestCase):
    def test_get_positions_all(self):
        fund = TickerFactory.create(unit_price=2.1)
        fund2 = TickerFactory.create(unit_price=4)
        goal = GoalFactory.create()
        today = date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        order1 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec1 = Execution.objects.create(asset=fund,
                                         volume=10,
                                         order=order1,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=20)
        t1 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=20)
        dist1 = ExecutionDistributionFactory.create(execution=exec1, transaction=t1, volume=10)
        PositionLotFactory(quantity=10, execution_distribution=dist1)

        order2 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec2 = Execution.objects.create(asset=fund,
                                         volume=5,
                                         order=order2,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=10)
        t2 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=10)
        dist2 = ExecutionDistributionFactory.create(execution=exec2, transaction=t2, volume=5)
        PositionLotFactory(quantity=5, execution_distribution=dist2)

        order3 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec3 = Execution.objects.create(asset=fund2,
                                         volume=1,
                                         order=order3,
                                         price=2,
                                         executed=date(2014, 6, 1),
                                         amount=4)
        t3 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=date(2014, 6, 1),
                                       amount=4)
        dist3 = ExecutionDistributionFactory.create(execution=exec3, transaction=t3, volume=1)
        PositionLotFactory(quantity=1, execution_distribution=dist3)

        positions = goal.get_positions_all()

        self.assertTrue(positions[0]['quantity'] == 15)
        self.assertTrue(positions[1]['quantity'] == 1)

    def test_sum_stocks_for_goal(self):
        self.content_type = ContentTypeFactory.create()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.BONDS.get())
        self.stocks_asset_class = AssetClassFactory.create(investment_type=InvestmentType.Standard.STOCKS.get())
        fund1 = TickerFactory.create(asset_class=self.stocks_asset_class,
                                     benchmark_content_type=self.content_type,
                                     etf=True)
        goal = GoalFactory.create()

        order = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec = Execution.objects.create(asset=fund1,
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
        dist = ExecutionDistributionFactory.create(execution=exec, transaction=t1, volume=10)
        PositionLotFactory(quantity=10, execution_distribution=dist)
        weight_stocks = goal.stock_balance
        weight_bonds = goal.bond_balance
        weight_core = goal.core_balance
        self.assertTrue(weight_stocks == 100)
        self.assertTrue(weight_bonds == 0)
        self.assertTrue(weight_core == 100)


class GoalTotalReturnTest(TestCase):
    # FIXME this doesn't work because of using Fixture1
    # fixtures = 'main/tests/fixtures/transactions.json',

    def load_fixture(self, *names):
        for db_name in self._databases_names(include_mirrors=False):
            call_command('loaddata', *names,
                         **{'verbosity': 0, 'database': db_name})

    begin_date = datetime(2016, 6, 25, 11, 0, 0, tzinfo=timezone.utc)

    def mocked_date(self, days):
        return mock.Mock(return_value=self.begin_date + timedelta(days))

    def goal_opening(self, value):
        with mock.patch.object(timezone, 'now', self.mocked_date(0)):
            self.goal = Fixture1.goal1()
            Transaction.objects.create(reason=Transaction.REASON_DEPOSIT,
                                       to_goal=self.goal, amount=value,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=timezone.now())

    def goal_transaction(self, amount, days, withdrawal=False):
        with mock.patch.object(timezone, 'now', self.mocked_date(days)):
            data = {
                'amount': amount,
                'status': Transaction.STATUS_EXECUTED,
                'executed': timezone.now(),
            }
            if withdrawal:
                data.update({
                    'reason': Transaction.REASON_WITHDRAWAL,
                    'from_goal': self.goal,
                })
            else:
                data.update({
                    'reason': Transaction.REASON_DEPOSIT,
                    'to_goal': self.goal,
                })
            Transaction.objects.create(**data)
            self.goal.cash_balance = self.goal.requested_incomings - self.goal.requested_outgoings

    def total_return(self, days, closing_balance):
        self.goal.cash_balance = closing_balance
        with mock.patch('main.finance.now', self.mocked_date(days)):
            return self.goal.total_return

    def closing_balance(self, days):
        with mock.patch.object(timezone, 'now', self.mocked_date(days)):
            return self.goal.total_balance

    def test_zero_balance(self):
        goal = Fixture1.goal1()
        self.load_fixture('main/tests/fixtures/transactions.json')
        with mock.patch('main.finance.now', self.mocked_date(0)):
            total_return = goal.total_return
        self.assertEqual(total_return, -1.0)

    def test_one(self):
        """
        opening balance of 1000
        closing balance of 1100
        no transactions
        time period of 1.5 years
        """
        self.goal_opening(1000)
        total_return = self.total_return(548, 1100)  # 1.5y
        self.assertEqual(total_return, 0.06558679242281773)

    def test_two(self):
        """
        opening of 1000
        deposit at 8 months of 200
        closing of 1100
        time period of 1.5 years
        """
        self.goal_opening(1000)
        self.goal_transaction(200, 8 * 30)  # 8m
        total_return = self.total_return(548, 1100)  # 1.5y
        self.assertEqual(total_return, -0.06085233384111588)

    def test_three(self):
        """
        opening of 1000
        withdrawal at 8 months of 200
        closing of 1100
        time period of 1.5 years
        """
        self.goal_opening(1000)
        self.goal_transaction(200, 8 * 30, True)  # 8m
        total_return = self.total_return(548, 1100)  # 1.5y
        self.assertEqual(total_return, 0.21418097150518434)

    def test_four(self):
        """
        opening balance of 1000
        closing balance of 900
        no transactions
        time period of 1.5 years
        """
        self.goal_opening(1000)
        total_return = self.total_return(548, 900)  # 1.5y
        self.assertEqual(total_return, -0.0678153128925949)

    def test_five(self):
        """
        opening balance of 1000
        closing balance of 900
        no transactions
        time period of 8 months
        """
        self.goal_opening(1000)
        total_return = self.total_return(8 * 30, 900)  # 8m
        self.assertEqual(total_return, -0.14815060547446401)

    def test_amount_achieved(self):
        """
        ensure completion does not affect a goal's ability to
        continue with the same parameters
        """
        self.goal_opening(10000)
        with mock.patch.object(timezone, 'now', self.mocked_date(0)):
            self.assertEqual(self.goal.amount_achieved, False)

        self.goal_transaction(90000, 365)
        with mock.patch.object(timezone, 'now', self.mocked_date(365)):
            self.assertEqual(self.goal.amount_achieved, True)

        self.goal_transaction(50000, 365*2)
        with mock.patch.object(timezone, 'now', self.mocked_date(365)):
            self.assertEqual(self.goal.amount_achieved, True)

    def test_zero_target(self):
        self.goal_opening(10000)
        self.load_fixture('main/tests/fixtures/transactions.json')
        self.goal.selected_settings.target = 0
        self.goal.selected_settings.completion_date = self.goal.created
        self.assertEqual(self.goal.amount_achieved, True)
        self.assertEqual(self.goal.on_track, True)

    def test_goal_completion(self):
        self.goal_opening(100)
        self.goal_transaction(200, 365)
        self.goal.selected_settings.target = 300
        with mock.patch.object(timezone, 'now', self.mocked_date(365)):
            self.assertEqual(self.goal.amount_achieved, True)
            # What can we do here to test portfolio optimisation? -- Lee
