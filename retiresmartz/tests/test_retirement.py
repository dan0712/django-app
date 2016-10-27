import datetime

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from retiresmartz.calculator import Calculator
from retiresmartz.calculator.assets import TaxDeferredAccount, TaxPaidAccount
from retiresmartz.calculator.cashflows import AccountContribution, JobIncome, \
    ReverseMortgage, SocialSecurity
from retiresmartz.calculator.desired_cashflows import RetirementDesiredCashFlow
from retiresmartz.models import InflationForecast, InflationForecastImport


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

        calc.add_assets(acc_saving, acc_401k)

        house = ReverseMortgage(250000, ret_date, ret_years)
        job_income = JobIncome(2000, stop_work_day)
        ss_payments = SocialSecurity(birthday, ret_date)

        calc.add_cash_flows(house, job_income, ss_payments)

        rdcf = RetirementDesiredCashFlow(4000, ret_date, ret_years)
        asset_values, income_values = calc.calculate(rdcf)

        self.assertEqual(list(asset_values.columns.values),
                         ['Saving', '401k'])
        self.assertEqual(list(income_values.columns.values),
                         ['desired', 'actual'])
        self.assertEqual(len(asset_values.values), 181)
        self.assertEqual(len(income_values.values), 181)


class InflationForecastModelTest(TestCase):
    def test_loader(self):
        data = (0.020619787, 0.017658812, 0.01676485, 0.01646296, 0.016408307,
                0.016477804, 0.016615633, 0.016792673, 0.016992324, 0.01720454,
                0.017422986, 0.017643544, 0.017863485, 0.018080979,
                0.018294792, 0.018504101, 0.018708364, 0.018907242,
                0.019100536, 0.019288151, 0.019470068, 0.01964632, 0.019816982,
                0.019982156, 0.020141964, 0.020296542, 0.020446037,
                0.020590602, 0.02073039, 0.020865559,)
        imp = InflationForecastImport(date=datetime.date(2016, 1, 1))
        imp.load(2016, data)

        self.assertEqual(InflationForecast.objects.count(), len(data) * 12)
