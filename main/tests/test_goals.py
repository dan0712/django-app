from django.core.exceptions import ValidationError
from django.test import TestCase

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
