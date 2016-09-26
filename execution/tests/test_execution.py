from datetime import datetime
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone

from execution.account_groups.account_allocations import AccountAllocations
from execution.account_groups.account_allocations import Execution as ExecutionClass
from execution.broker.ibroker import IBroker
from execution.broker.interactive_brokers.end_of_day.end_of_day import create_django_executions
from execution.broker.interactive_brokers.order.order import Order, OrderStatus
from execution.data_structures.market_depth import MarketDepth, SingleLevelMarketDepth
from execution.end_of_day import *
from execution.end_of_day import get_execution_requests, transform_execution_requests
from main.models import ExternalInstrument, InvestmentType
from main.tests.fixture import Fixture1
from api.v1.tests.factories import ExecutionRequestFactory, MarketOrderRequestFactory, ClientAccountFactory, GoalFactory, TickerFactory

class BaseTest(TestCase):
    def setUp(self):
        self.account = ClientAccountFactory.create()
        self.goal = GoalFactory.create(account=self.account)
        self.mor = MarketOrderRequestFactory.create(account=self.account)

        self.asset = TickerFactory.create()
        self.asset2 = TickerFactory.create()
        er1 = ExecutionRequestFactory.create(goal=self.goal, asset=self.asset, volume=5, order=self.mor)
        er2 = ExecutionRequestFactory.create(goal=self.goal, asset=self.asset, volume=10, order=self.mor)
        er3 = ExecutionRequestFactory.create(goal=self.goal, asset=self.asset2, volume=10, order=self.mor)


    def test_execution_requests_with_market_order_request(self):

        requests = ExecutionRequest.objects.all().filter(order=self.mor)
        self.assertTrue(requests[0].volume == 5)
        self.assertTrue(requests[1].volume == 10)

    def test_apex_order1(self):
        create_apex_orders()
        apex_orders = ApexOrder.objects.all()
        self.assertTrue(apex_orders[0].ticker.id == self.asset.id)
        self.assertTrue(apex_orders[0].volume == 15)
        self.assertTrue(apex_orders[1].ticker.id == self.asset2.id)
        self.assertTrue(apex_orders[1].volume == 10)

    def test_apex_order2(self):
        self.account2 = ClientAccountFactory.create()
        self.goal2 = GoalFactory.create(account=self.account2)
        self.mor2 = MarketOrderRequestFactory.create(account=self.account2)
        self.asset3 = TickerFactory.create()
        er4 = ExecutionRequestFactory.create(goal=self.goal2, asset=self.asset3, volume=20, order=self.mor2)
        create_apex_orders()
        apex_orders = ApexOrder.objects.all()
        self.assertTrue(len(apex_orders) == 3)
        self.assertTrue(apex_orders[2].volume == 20)

    def test_apex_order3(self):
        self.account3 = ClientAccountFactory.create()
        self.goal3 = GoalFactory.create(account=self.account3)
        self.mor3 = MarketOrderRequestFactory.create(account=self.account3)
        er5 = ExecutionRequestFactory.create(goal=self.goal3, asset=self.asset, volume=20, order=self.mor3)
        create_apex_orders()
        apex_orders = ApexOrder.objects.all()
        self.assertTrue(len(apex_orders) == 2)
        self.assertTrue(apex_orders[0].volume == 35)



