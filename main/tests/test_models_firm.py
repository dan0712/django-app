# -*- coding: utf-8 -*-
from django.test import TestCase
from api.v1.tests.factories import FirmFactory, FiscalYearFactory, \
    AdvisorFactory, ClientFactory, ClientAccountFactory, TransactionFactory, \
    GoalFactory, AccountTypeRiskProfileGroupFactory
from datetime import datetime, date
from main.models import Transaction
from main import constants
from dateutil.relativedelta import relativedelta


class FirmModelTests(TestCase):
    def setUp(self):
        for atid, _ in constants.ACCOUNT_TYPES:
            AccountTypeRiskProfileGroupFactory.create(account_type=atid)
        self.today = today = date(2016, 5, 1)
        self.older_fiscal_year = FiscalYearFactory.create()
        self.older_fiscal_year2 = FiscalYearFactory.create()
        self.current_fiscal_year = FiscalYearFactory.create(year=today.year,
                                                            begin_date=datetime(year=today.year,
                                                                                month=1,
                                                                                day=1),
                                                            end_date=datetime(year=today.year,
                                                                              month=12,
                                                                              day=31))
        self.firm = FirmFactory.create()
        self.firm.fiscal_years.add(self.older_fiscal_year)
        self.firm.fiscal_years.add(self.older_fiscal_year2)
        self.firm.fiscal_years.add(self.current_fiscal_year)
        # add an advisor for the firm
        self.advisor = AdvisorFactory.create(firm=self.firm)
        # add a client account for the firm
        self.betasmartz_client = ClientFactory.create(advisor=self.advisor)
        self.client_account = ClientAccountFactory.create(primary_owner=self.betasmartz_client)
        # add some goals
        self.goal1 = GoalFactory.create(account=self.client_account)
        self.goal2 = GoalFactory.create(account=self.client_account)
        # add some transaction fees associated with the goals
        # there are two fees here, one for the from_goal1, and one for the to_goal2
        self.fee1 = TransactionFactory.create(reason=Transaction.REASON_FEE,
                                              status=Transaction.STATUS_EXECUTED,
                                              from_goal=self.goal1, to_goal=self.goal2,
                                              amount=500,
                                              executed=today - relativedelta(months=1))

        # add new advisor to firm
        # add new clientacounts for advisor and fees
        self.advisor2 = AdvisorFactory.create(firm=self.firm)
        self.betasmartz_client2 = ClientFactory.create(advisor=self.advisor2)
        self.client_account2 = ClientAccountFactory.create(primary_owner=self.betasmartz_client2)
        self.goal3 = GoalFactory.create(account=self.client_account2)
        # add some more fees
        self.fee2 = TransactionFactory.create(reason=Transaction.REASON_FEE,
                                              status=Transaction.STATUS_EXECUTED,
                                              to_goal=self.goal3,
                                              amount=800,
                                              executed=self.older_fiscal_year.begin_date + relativedelta(months=1))

    def current_fiscal_year(self):
        self.assertNotEqual(self.firm.get_current_fiscal_year(),
                            self.older_fiscal_year)
        self.assertEqual(self.firm.get_current_fiscal_year(),
                         self.current_fiscal_year)

    def test_fees_ytd(self):
        expected_fees_ytd = self.fee1.amount * 2
        # check setUp fees match expected
        self.assertEqual(self.firm.fees_ytd, expected_fees_ytd)
        # add new fee and check new estimate matches expectation
        new_fee = TransactionFactory.create(reason=Transaction.REASON_FEE,
                                            status=Transaction.STATUS_EXECUTED,
                                            to_goal=self.goal1,
                                            amount=100,
                                            executed=self.today - relativedelta(days=5))
        self.assertEqual(self.firm.fees_ytd, new_fee.amount + expected_fees_ytd)

    def test_total_fees(self):
        # one charge for to_goal, one charge for from_goal
        expected_total_fees = self.fee2.amount + (self.fee1.amount * 2)
        self.assertEqual(self.firm.total_fees, expected_total_fees)
