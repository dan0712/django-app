import datetime
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from main.models import Goal
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

mocked_now = mock.Mock(return_value=datetime.datetime(2016, 6, 25, 11, 0, 0,
                                                      tzinfo=timezone.utc))
class GoalTotalReturnTest(TestCase):
    # FIXME this doesn't work because of using Fixture1
    # fixtures = 'main/tests/fixtures/transactions.json',

    def load_fixture(self, *names):
        for db_name in self._databases_names(include_mirrors=False):
            call_command('loaddata', *names,
                         **{'verbosity': 0, 'database': db_name})

    def test_total_return(self):
        goal = Fixture1.goal1()
        self.load_fixture('main/tests/fixtures/transactions.json')
        with mock.patch('main.models.now', mocked_now):
            total_return = goal.total_return
        self.assertEqual(total_return, -0.7741935483870968)
