from main.tests.fixtures import Fixture1
from django.test import TestCase
from execution.end_of_day import *
import unittest
from unittest.mock import Mock
from execution.broker.ibroker import IBroker


class BaseTest(TestCase):

    def setUp(self):
        self.con = Mock(IBroker)
        self.con.return_value = True
        short_sleep()

    def test_ib_connect(self):
        connected = self.con.connect()
        short_sleep()
        self.assertTrue(connected)

    def test_change_account_cash(self):
        goal1 = Fixture1.goal1()
        account = Fixture1.personal_account1()
        account.all_goals.return_value = [goal1]

        #no difference
        account.cash_balance = 1000
        ib_account_cash[account.account_id] = 1000
        difference = reconcile_cash_client_account(account)
        self.assertAlmostEqual(0, difference)

        #deposit - transferred to account.cash_balance
        ib_account_cash[account.account_id] = 1100
        reconcile_cash_client_account(account)
        self.assertAlmostEqual(1100, account.cash_balance)

        #withdrawal - from account.cash_balance
        ib_account_cash[account.account_id] = 900
        reconcile_cash_client_account(account)
        self.assertAlmostEqual(900, account.cash_balance)

        #exception - sum of goal cash balances < ib_account_cash
        goal1.cash_balance = 1000
        account.cash_balance = 100
        ib_account_cash[account.account_id] = 900
        self.assertRaises(Exception, reconcile_cash_client_account(account))







