from django.test import TestCase

from main.risk_profiler import recommend_risk, max_risk, NEUTRAL_RISK
from main.tests.fixture import Fixture1


class RiskProfilerTests(TestCase):
    def test_recommend_risk_no_questions(self):
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        account = settings.goal.account
        self.assertEqual(recommend_risk(settings), 0.5)

    def test_recommend_risk_fully_unanswered(self):
        # Populate the questions, we should still get 0.5
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        account = settings.goal.account
        Fixture1.populate_risk_profile_questions()
        self.assertEqual(recommend_risk(settings), 0.5)

    def test_recommend_risk_partially_unanswered(self):
        # Partially populate the answers, we should still get 0.5
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        account = settings.goal.account
        Fixture1.populate_risk_profile_questions()
        Fixture1.risk_profile_answer1a()
        self.assertEqual(recommend_risk(settings), 0.5)

    def test_recommend_risk_fully_answered_bad_questions(self):
        # Fully populate the answers, but no range in the available question responses, we should get 0.5
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        account = settings.goal.account
        Fixture1.populate_risk_profile_questions()  # Also populates all possible answers.
        Fixture1.populate_risk_profile_responses()

        Fixture1.risk_profile_question3() # Add a question we don't have an answer for
        self.assertEqual(recommend_risk(settings), 0.5)

        # Now answer the question, we shouldn't get NEUTRAL
        account.primary_owner.risk_profile_responses.add(Fixture1.risk_profile_answer3a())
        self.assertNotEqual(recommend_risk(settings), NEUTRAL_RISK)

    def test_recommend_risk_fully_answered(self):
        # Fully populate the answers, we should get 0.5
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        Fixture1.populate_risk_profile_questions()  # Also populates all possible answers.
        Fixture1.populate_risk_profile_responses()
        self.assertEqual(recommend_risk(settings), 1.0)

    def test_recommend_risk_no_weights(self):
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        self.assertEqual(recommend_risk(settings), 0.5)

    def test_recommend_risk(self):
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        client = goal.account.primary_owner
        # Add the weights for the risk factors
        Fixture1.populate_risk_profile_questions()  # Also populates all possible answers.
        Fixture1.populate_risk_profile_responses()

        # First lets start with the test_client, who scored 9 for all B,A,S

        # A goal of 80% of the value on a all-9s account is a bad idea
        # It's the lowest possible score
        settings.goal.account.primary_owner.net_worth = 100
        settings.goal.cash_balance = 80
        self.assertAlmostEqual(recommend_risk(settings), 0.55, 2)

        # A goal of 50% of the value is just as bad
        settings.goal.account.primary_owner.net_worth = 100
        settings.goal.cash_balance = 50
        self.assertAlmostEqual(recommend_risk(settings), 0.55, 2)

        # A goal of 10% of the value on a all-9s account is 1.0
        # meaning this is the safest possible bet
        settings.goal.account.primary_owner.net_worth = 100
        settings.goal.cash_balance = 10
        self.assertAlmostEqual(recommend_risk(settings), 1.0, 2)

        # A goal of 33% of the value on a all-9s account is about 0.5
        # Even if you are risky, sophisticated and rich, 30% is a lot
        settings.goal.account.primary_owner.net_worth = 100
        settings.goal.cash_balance = 33
        self.assertAlmostEqual(recommend_risk(settings), 0.75, 1)

        # For a new investor, the best possible suggestion is 10% or less
        settings.goal.account.primary_owner.net_worth = 100
        settings.goal.cash_balance = 10
        client.risk_profile_responses.clear()
        client.risk_profile_responses.add(Fixture1.risk_profile_answer1b())
        client.risk_profile_responses.add(Fixture1.risk_profile_answer2b())
        self.assertAlmostEqual(recommend_risk(settings), 0.2, 1)

    def test_max_risk(self):
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        client = goal.account.primary_owner
        # Add the weights for the risk factors
        Fixture1.populate_risk_profile_questions()  # Also populates all possible answers.
        Fixture1.populate_risk_profile_responses()

        # we haven't set a net worth or a target, so worth_score isn't a factor

        # An all-9s account will have a max_risk of 1
        self.assertEqual(max_risk(settings), 1.0)

        # and if they are low risk behavior, high Ability + Sophistication
        # the max risk is still 1
        client.risk_profile_responses.clear()
        client.risk_profile_responses.add(Fixture1.risk_profile_answer1c())
        client.risk_profile_responses.add(Fixture1.risk_profile_answer2c())
        self.assertEqual(max_risk(settings), 1.0)

        # but if they are risky, new and unskilled, recommend no risk
        client.risk_profile_responses.clear()
        client.risk_profile_responses.add(Fixture1.risk_profile_answer1d())
        client.risk_profile_responses.add(Fixture1.risk_profile_answer2d())
        self.assertAlmostEqual(recommend_risk(settings), 0.1, 1)
        self.assertAlmostEqual(max_risk(settings), 0.1, 1)
