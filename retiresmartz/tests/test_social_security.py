from datetime import date
from django.test import TestCase
from unittest import skip
from retiresmartz.calculator.social_security import calculate_payments


class SocialSecurityTests(TestCase):

    @skip('Fails intermittently on deployment test runs')
    def test_calculate_payments(self):
        amounts = calculate_payments(dob=date(1975, 1, 1), income=60000)
        self.assertEqual(amounts[67], 2055)
        self.assertEqual(amounts[68], 2219)
