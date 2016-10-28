import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from common.utils import months_between
from main.models import Inflation
from retiresmartz.calculator.cashflows import InflatedCashFlow, ReverseMortgage, EmploymentIncome


class CashFlowTests(TestCase):
    def setUp(self):
        self.dob = datetime.date(1960, 3, 14)
        self.today = datetime.date(2016, 2, 1)
        self.retirement = datetime.date(2029, 2, 1)
        self.death = datetime.date(2054, 6, 1)

        # Populate some inflation figures.
        dt = datetime.date(1950, 1, 1)
        inflations = []
        while dt <= self.death:
            inflations.append(Inflation(year=dt.year, month=dt.month, value=0.001))
            dt += relativedelta(months=1)
        if hasattr(Inflation, '_cum_data'):
            del Inflation._cum_data
        Inflation.objects.bulk_create(inflations)

    def test_inflated_cash_flow(self):
        cf = InflatedCashFlow(amount=116,
                              today=self.today,
                              start_date=self.retirement,
                              end_date=self.dob + relativedelta(years=85))

        # Make sure we can use the calculator as of today
        self.assertEqual(cf.on(self.today), 0)

        # Make sure before start_date is zero
        self.assertEqual(cf.on(self.retirement - relativedelta(days=1)), 0)

        # Make sure it starts on start date, and was inflated correctly
        ret_val = cf.on(self.retirement)
        self.assertAlmostEqual(ret_val, 116 * 1.001 ** months_between(self.today, self.retirement), 4)

        # Make sure we can get end date and it is inflated correctly
        self.assertAlmostEqual(cf.on(self.dob + relativedelta(years=85)),
                               116 * 1.001 ** months_between(self.today, self.dob + relativedelta(years=85)),
                               4)

        # Make sure after end date it returns zero
        self.assertEqual(cf.on(self.dob + relativedelta(years=85, days=1)), 0)

        # Make sure backwards dates raise a value error
        with self.assertRaises(ValueError):
            cf.on(self.retirement)

        # Make sure a reset allows previous dates again, and we get the same result
        cf.reset()
        self.assertEqual(ret_val, cf.on(self.retirement))

    def test_reverse_mortgage(self):
        cf = ReverseMortgage(home_value=200000,
                             value_date=self.today,
                             start_date=self.retirement,
                             end_date=self.death)

        # Make sure we can use the calculator as of today
        self.assertEqual(cf.on(self.today), 0)

        # Make sure before start_date is zero
        self.assertEqual(cf.on(self.retirement - relativedelta(days=1)), 0)

        # Make sure it starts on start date, and was inflated correctly
        ret_val = cf.on(self.retirement)
        payments = months_between(self.retirement, self.death)
        self.assertAlmostEqual(ret_val,
                               200000 * 1.001 ** months_between(self.today, self.retirement) / payments * 0.9,
                               4)

        # Make sure we can get end date and it is the same payment
        self.assertAlmostEqual(cf.on(self.death), ret_val, 4)

        # Make sure after end date it returns zero
        self.assertEqual(cf.on(self.death + relativedelta(days=1)), 0)

        # Make sure backwards dates raise a value error
        with self.assertRaises(ValueError):
            cf.on(self.retirement)

        # Make sure a reset allows previous dates again, and we get the same result
        cf.reset()
        self.assertEqual(ret_val, cf.on(self.retirement))

    def test_employment_income(self):
        cf = EmploymentIncome(income=4000,
                              growth=0.01,
                              today=self.today,
                              end_date=self.retirement)

        # Make sure we can use the calculator as of today
        self.assertEqual(cf.on(self.today), 4000)

        # Make sure we can get it on the end date and it is inflated correctly
        predicted = 4000 * (((1.01 ** (1/12)) + 0.001) ** months_between(self.today, self.retirement))
        self.assertAlmostEqual(cf.on(self.retirement), predicted, 4)

        # Make sure after end date it returns zero
        self.assertEqual(cf.on(self.death + relativedelta(days=1)), 0)

        # Make sure backwards dates raise a value error
        with self.assertRaises(ValueError):
            cf.on(self.retirement)

        # Make sure a reset allows previous dates again, and we get the same result
        cf.reset()
        self.assertAlmostEqual(predicted, cf.on(self.retirement), 4)
