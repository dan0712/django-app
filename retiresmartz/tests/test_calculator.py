import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from main.models import Inflation
from retiresmartz.calculator import Calculator
from retiresmartz.calculator.assets import TaxDeferredAccount, TaxPaidAccount
from retiresmartz.calculator.cashflows import ReverseMortgage, InflatedCashFlow, EmploymentIncome
from retiresmartz.calculator.desired_cashflows import RetiresmartzDesiredCashFlow


class CalculatorTest(TestCase):
    def setUp(self):
        self.today = datetime.date(2016, 2, 1)
        self.retirement = datetime.date(2029, 2, 1)
        self.death = datetime.date(2054, 6, 1)

        # Populate some inflation figures.
        dt = datetime.date(1950, 1, 1)
        inflations = []
        while dt <= self.death:
            inflations.append(Inflation(year=dt.year, month=dt.month, value=0.001))
            dt += relativedelta(months=1)
        Inflation.objects.bulk_create(inflations)

    def test_calculate(self):
        dob = datetime.date(1960, 3, 14)

        # Pre-retirement income cash flow
        income_calc = EmploymentIncome(income=4000,
                                       growth=0.01,
                                       today=self.today,
                                       end_date=self.retirement)

        # Retirement Assets
        acc_rothIRA = TaxPaidAccount('RothIRA', self.today, 50000, 0.05, self.retirement, self.death, 400)
        acc_401k = TaxDeferredAccount(dob, 0.1, '401k', self.today, 150000, 0.05, self.retirement, self.death, 200)

        # Retirement Cash Flows
        house = ReverseMortgage(250000, self.today, self.retirement, self.death)
        retirement_income = InflatedCashFlow(116, self.today, self.retirement, dob + relativedelta(years=85))
        ss_payments = InflatedCashFlow(1433, self.today, self.retirement, self.death)

        # I want a Luxury retirement. 1.5 * Current income.
        rdcf = RetiresmartzDesiredCashFlow(income_calc, 6000, self.today, self.retirement, self.death)

        calc = Calculator([rdcf, house, retirement_income, ss_payments], [acc_rothIRA, acc_401k])

        asset_values, income_values = calc.calculate(rdcf)

        self.assertEqual(list(asset_values.columns.values), ['RothIRA', '401k'])
        self.assertEqual(list(income_values.columns.values), ['desired', 'actual'])
        # TODO: Actually test the calculator is working properly
        self.assertEqual(len(asset_values.values), 460)
        self.assertEqual(len(income_values.values), 460)
