from django.test import TestCase

from main.risk_profiler import get_risk_willingness, recommend_risk
from main.tests.fixture import Fixture1


class RiskProfilerTests(TestCase):
    def test_willingness_no_questions(self):
        account = Fixture1.personal_account1()
        self.assertEqual(get_risk_willingness(account), 0.5)

    def test_willingness_fully_unanswered(self):
        # Populate the questions, we should still get 0.5
        Fixture1.populate_risk_profile_questions()
        account = Fixture1.personal_account1()
        self.assertEqual(get_risk_willingness(account), 0.5)

    def test_willingness_partially_unanswered(self):
        # Partially populate the answers, we should still get 0.5
        Fixture1.populate_risk_profile_questions()
        Fixture1.risk_profile_answer1a()
        account = Fixture1.personal_account1()
        self.assertEqual(get_risk_willingness(account), 0.5)

    def test_willingness_fully_answered_bad_questions(self):
        # Fully populate the answers, but no range in the available question responses, we should get 0.5
        account = Fixture1.personal_account1()
        account.risk_profile_responses.add(Fixture1.risk_profile_answer1a())
        self.assertEqual(get_risk_willingness(account), 0.5)

    def test_willingness_fully_answered(self):
        # Fully populate the answers, we should get 0.5
        Fixture1.populate_risk_profile_questions()  # Also populates all possible answers.
        Fixture1.populate_risk_profile_responses()
        account = Fixture1.personal_account1()
        self.assertEqual(get_risk_willingness(account), 1.0)

    def test_recommend_risk_no_weights(self):
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        self.assertEqual(recommend_risk(settings), 0.5)

    def test_recommend_risk(self):
        goal = Fixture1.goal1()
        settings = Fixture1.settings1()
        # Add the weights for the risk factors
        t = Fixture1.goal_type1()
        t.risk_factor_weights = {'ttl': 5,
                                 'age': 7,
                                 'status': 6,
                                 'income': 5,
                                 'worth': 10}
        t.save()
        self.assertAlmostEqual(recommend_risk(settings), 0.15677, 5)
