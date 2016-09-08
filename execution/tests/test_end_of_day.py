from main.tests.fixture import Fixture1
from django.test import TestCase
from execution.end_of_day import *
from unittest.mock import Mock
from execution.broker.ibroker import IBroker
from execution.data_structures.market_depth import MarketDepth, SingleLevelMarketDepth
from datetime import datetime
from execution.end_of_day import get_execution_requests, transform_execution_requests
from execution.account_groups.account_allocations import AccountAllocations, Execution
from execution.account_groups.create_account_groups import FAAccountProfile
from django.utils import timezone


class BaseTest(TestCase):

    def setUp(self):
        self.con = Mock(IBroker)
        self.con.connect.return_value = True

        self.con.requesting_market_depth.return_value = False

        self.con.market_data = dict()
        self.con.market_data['GOOG'] = MarketDepth()

        single_level = SingleLevelMarketDepth()
        single_level.bid = 1
        single_level.ask = 2
        single_level.bid_volume = 50
        single_level.ask_volume = 100
        self.con.market_data['GOOG'].add_level(0, single_level)

        Fixture1.personal_account1()
        Fixture1.personal_account2()

        request1 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.PENDING.value,
                                                     account=Fixture1.personal_account1())

        request2 = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.APPROVED.value,
                                                     account=Fixture1.personal_account2())
        Fixture1.ib_account1()
        Fixture1.ib_account2()

        params = {
            'reason': ExecutionRequest.Reason.DRIFT.value,
            'goal': Fixture1.goal1(),
            'asset': Fixture1.fund3(),
            'volume': 5,
            'order': request1
        }
        ExecutionRequest.objects.get_or_create(id=1, defaults=params)

        params = {
            'reason': ExecutionRequest.Reason.DRIFT.value,
            'goal': Fixture1.goal1(),
            'asset': Fixture1.fund4(),
            'volume': 5,
            'order': request1
        }
        ExecutionRequest.objects.get_or_create(id=2, defaults=params)

        #Client2
        params = {
            'reason': ExecutionRequest.Reason.DRIFT.value,
            'goal': Fixture1.goal2(),
            'asset': Fixture1.fund3(),
            'volume': 10,
            'order': request2
        }
        ExecutionRequest.objects.get_or_create(id=3, defaults=params)
        params = {
            'reason': ExecutionRequest.Reason.DRIFT.value,
            'goal': Fixture1.goal2(),
            'asset': Fixture1.fund4(),
            'volume': 10,
            'order': request2
        }
        ExecutionRequest.objects.get_or_create(id=4, defaults=params)

    def test_ib_time(self):
        self.con.current_time.return_value = timezone.now()
        time = self.con.current_time()
        self.assertTrue(type(time) is datetime)

    def test_ib_connect(self):
        connected = self.con.connect()
        self.assertTrue(connected)

    def test_change_account_cash(self):
        goal1 = Fixture1.goal1()

        account = Fixture1.personal_account1()
        account.all_goals.return_value = [goal1]

        #no difference
        account.cash_balance = 1000
        ib_account = account.ib_account

        ib_account_cash[ib_account.ib_account] = 1000
        difference = reconcile_cash_client_account(account)
        self.assertAlmostEqual(0, difference)

        self.assertEqual(ib_account.ib_account, 'DU299694')

        #deposit - transferred to account.cash_balance
        ib_account_cash[ib_account.ib_account] = 1100
        reconcile_cash_client_account(account)
        self.assertAlmostEqual(1100, account.cash_balance)

        #withdrawal - from account.cash_balance
        ib_account_cash[ib_account.ib_account] = 900
        reconcile_cash_client_account(account)
        self.assertAlmostEqual(900, account.cash_balance)

        #exception - sum of goal cash balances > ib_account_cash
        goal1.cash_balance = 1000
        goal1.save()
        account.cash_balance = 100
        ib_account_cash[ib_account.ib_account] = 900

        with self.assertRaises(Exception) as cm:
            reconcile_cash_client_account(account)
        self.assertTrue(ib_account.ib_account in cm.exception.args[0])

    def test_market_depth(self):
        self.con.request_market_depth('GOOG')

        while self.con.requesting_market_depth():
            short_sleep()

        self.assertAlmostEquals(self.con.market_data['GOOG'].levels[0].get_mid(), 1.5)
        self.assertEqual(self.con.market_data['GOOG'].depth, 10)

        self.assertAlmostEquals(self.con.market_data['GOOG'].levels[0].bid_volume, 50)
        self.assertAlmostEquals(self.con.market_data['GOOG'].levels[0].ask_volume, 100)

    def test_get_execution_requests(self):
        execution_requests = get_execution_requests()
        self.assertTrue(len(execution_requests) == 4)

    def test_transform_execution_requests(self):
        execution_requests = get_execution_requests()
        allocations = transform_execution_requests(execution_requests)
        self.assertTrue(allocations['SPY']['DU299694'] == 5)
        self.assertTrue(allocations['SPY']['DU299695'] == 10)
        self.assertTrue(allocations['TLT']['DU299694'] == 5)
        self.assertTrue(allocations['TLT']['DU299695'] == 10)

    def test_allocations(self):
        execution = Execution(10, 'DU299694', 5, timezone.now(), 1)

        allocation = AccountAllocations()

        allocation.add_execution_allocation(execution)

        self.assertTrue(allocation.allocations[1]['DU299694'].price == 10)
        self.assertTrue(allocation.allocations[1]['DU299694'].shares == 5)

        execution = Execution(20, 'DU299694', 5, timezone.now(), 1)
        allocation.add_execution_allocation(execution)

        self.assertTrue(allocation.allocations[1]['DU299694'].price == 15)
        self.assertTrue(allocation.allocations[1]['DU299694'].shares == 10)

    def test_create_account_groups(self):
        account_profile = FAAccountProfile()

        account_dict = {
            'DU299694': 5,
            'DU299695': 10,
        }

        account_profile.append_share_allocation('MSFT', account_dict)
        profile = account_profile.get_profile()

        profile_should_be = '<?xml version="1.0" encoding="UTF-8"?><ListOfAllocationProfiles><AllocationProfile><name>MSFT</name><type>3</type><ListOfAllocations varName="listOfAllocations"><Allocation><acct>DU299694</acct><amount>5.0</amount></Allocation><Allocation><acct>DU299695</acct><amount>10.0</amount></Allocation></ListOfAllocations></AllocationProfile></ListOfAllocationProfiles>'
        self.assertTrue(profile == profile_should_be)



