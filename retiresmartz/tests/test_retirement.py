import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from retiresmartz.calculator import Calculator
from retiresmartz.calculator.assets import TaxDeferredAccount, TaxPaidAccount
from retiresmartz.calculator.cashflows import AccountContribution, JobIncome, \
    ReverseMortgage, SocialSecurity
from retiresmartz.calculator.desired_cashflows import RetirementDesiredCashFlow


class CalculatorTest(TestCase):
    def test_general(self):
        birthday = datetime.date(1960, 3, 14)
        ret_date = datetime.date(2034, 2, 1)
        stop_work_day = birthday + relativedelta(years=65)
        ret_years = 15

        calc = Calculator(birthday)

        acc_saving = TaxPaidAccount('Saving', 50000, ret_date, ret_years)
        acc_saving.add_contributions(
            AccountContribution(4000, .1, stop_work_day),  # employee
            AccountContribution(4000, .1, stop_work_day),  # employer
        )

        acc_401k = TaxDeferredAccount('401k', 150000, ret_date, ret_years)
        acc_401k.add_contributions(
            AccountContribution(4000, .05, stop_work_day),  # employee
            AccountContribution(4000, .05, stop_work_day),  # employer
        )

        calc.add_asset(acc_saving, acc_401k)

        house = ReverseMortgage(250000, ret_date, ret_years)
        job_income = JobIncome(2000, stop_work_day)
        ss_payments = SocialSecurity(birthday, ret_date)

        calc.add_cash_flow(house, job_income, ss_payments)

        rdcf = RetirementDesiredCashFlow(4000, ret_date, ret_years)
        asset_values, income_values = calc.calculate(rdcf)

        self.assertEqual(list(asset_values.columns.values),
                         ['Saving', '401k'])
        self.assertEqual(list(income_values.columns.values),
                         ['desired', 'actual'])
        self.assertEqual(len(asset_values.values), 181)
        self.assertEqual(len(income_values.values), 181)
