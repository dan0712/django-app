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
        account = ClientAccountFactory.create()
        goal = GoalFactory.create(account=account)
        self.mor = MarketOrderRequestFactory.create(account=account)

        asset = TickerFactory.create()
        asset2 = TickerFactory.create()
        er1 = ExecutionRequestFactory.create(goal=goal, asset=asset, volume=5, order=self.mor)
        er2 = ExecutionRequestFactory.create(goal=goal, asset=asset, volume=10, order=self.mor)
        er3 = ExecutionRequestFactory.create(goal=goal, asset=asset2, volume=10, order=self.mor)

    def test_execution_requests_with_market_order_request(self):
        requests = ExecutionRequest.objects.all().filter(order=self.mor)

        self.assertTrue(requests[0].volume == 5)
        self.assertTrue(requests[1].volume == 10)


    def test_market_order_request_apex(self):
        ers = create_apex_order()
        self.assertTrue(True)


    def test_apex_order(self):
        pass
