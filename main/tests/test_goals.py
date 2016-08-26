from datetime import datetime, timedelta
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from main.models import Goal, Transaction
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

    def total_return(self, days, closing_balance):
        self.goal.cash_balance = closing_balance
        with mock.patch('main.finance.now', self.mocked_date(days)):
            return self.goal.total_return

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
