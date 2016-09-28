from datetime import datetime
from unittest.mock import Mock

from django.test import TestCase
import numpy as np
from django.utils import timezone

from execution.account_groups.account_allocations import AccountAllocations
from execution.account_groups.account_allocations import Execution as ExecutionClass
from execution.broker.ibroker import IBroker
from execution.broker.interactive_brokers.end_of_day.end_of_day import create_django_executions
from execution.broker.interactive_brokers.order.order import Order, OrderStatus
from execution.data_structures.market_depth import MarketDepth, SingleLevelMarketDepth
from execution.end_of_day import *
from execution.end_of_day import get_execution_requests, transform_execution_requests
from main.models import ExternalInstrument, InvestmentType, ApexFill, ExecutionApexFill
from main.tests.fixture import Fixture1
from api.v1.tests.factories import ExecutionRequestFactory, MarketOrderRequestFactory, \
    ClientAccountFactory, GoalFactory, TickerFactory, ApexFillFactory, ApexOrderFactory, ExecutionFactory, ExecutionApexFillFactory, ExecutionDistributionFactory, TransactionFactory

from execution.end_of_day import create_apex_orders, create_executions_eds_transactions_from_apex_fills

from django.db.models import Sum, F
from django.db.models.functions import Coalesce

class BaseTest(TestCase):
    def setUp(self):
        self.account1 = ClientAccountFactory.create()
        self.goal1 = GoalFactory.create(account=self.account1)

        self.account2 = ClientAccountFactory.create()
        self.goal2 = GoalFactory.create(account=self.account2)

        self.account3 = ClientAccountFactory.create()
        self.goal3 = GoalFactory.create(account=self.account3)

        self.ticker1 = TickerFactory.create()
        self.ticker2 = TickerFactory.create()
        self.ticker3 = TickerFactory.create()

    def test_apex_fill_with_apex_order(self):
        order1 = ApexOrderFactory.create(volume=100)
        order2 = ApexOrderFactory.create(volume=200)

        ApexFillFactory.create(apex_order=order1, volume=100, price=1)
        ApexFillFactory.create(apex_order=order2, volume=100, price=1)
        ApexFillFactory.create(apex_order=order2, volume=100, price=1)

        fills = ApexFill.objects.filter(apex_order_id=order2).aggregate(sum=Sum('volume'))
        self.assertTrue(fills['sum'] == 200)

        fills = ApexFill.objects.filter(apex_order_id=order1).aggregate(sum=Sum('volume'))
        self.assertTrue(fills['sum'] == 100)

    def test_full_in_and_out_path1(self):
        #out
        mor = MarketOrderRequestFactory.create(account=self.account1)
        er = ExecutionRequestFactory.create(goal=self.goal1, asset=self.ticker1, volume=100, order=mor)
        create_apex_orders()

        #in
        fill1_volume = 50
        fill1_price = 10
        fill2_volume = 50
        fill2_price = 15
        order1 = ApexOrder.objects.get(ticker=self.ticker1)
        ApexFillFactory.create(apex_order=order1, volume=fill1_volume, price=fill1_price)
        ApexFillFactory.create(apex_order=order1, volume=fill2_volume, price=fill2_price)

        create_executions_eds_transactions_from_apex_fills()

        sum_volume = Execution.objects.filter(distributions__execution_request__goal=self.goal1)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 100)

    def test_full_in_and_out_path2(self):
        #out

        mor1 = MarketOrderRequestFactory.create(account=self.account1)
        er1 = ExecutionRequestFactory.create(goal=self.goal1, asset=self.ticker1, volume=100, order=mor1)

        mor2 = MarketOrderRequestFactory.create(account=self.account2)
        er2 = ExecutionRequestFactory.create(goal=self.goal2, asset=self.ticker2, volume=25, order=mor2)

        mor3 = MarketOrderRequestFactory.create(account=self.account3)
        er3 = ExecutionRequestFactory.create(goal=self.goal3, asset=self.ticker2, volume=25, order=mor3)

        create_apex_orders()

        #in
        fill1a_volume = 50
        fill1a_price = 10
        fill1b_volume = 50
        fill1b_price = 15

        order1 = ApexOrder.objects.get(ticker=self.ticker1)
        ApexFillFactory.create(apex_order=order1, volume=fill1a_volume, price=fill1a_price)
        ApexFillFactory.create(apex_order=order1, volume=fill1b_volume, price=fill1b_price)

        create_executions_eds_transactions_from_apex_fills()

        sum_volume = Execution.objects.filter(distributions__execution_request__goal=self.goal1)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 100)

        fill2_3_volume = 50
        fill2_3_price = 13
        order2_3 = ApexOrder.objects.get(ticker=self.ticker2)
        ApexFillFactory.create(apex_order=order2_3, volume=fill2_3_volume, price=fill2_3_price)

        create_executions_eds_transactions_from_apex_fills()
        sum_volume = Execution.objects.filter(distributions__execution_request__asset=self.ticker2)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 50)


        execution2 = ExecutionFactory.create(asset=order2_3.ticker,
                                             volume=25,
                                             price=fill2_3_price,
                                             amount=25 * fill2_3_price)
        ExecutionApexFillFactory.create(apex_fill=apex_fill2_3, execution=execution2)
        transaction2 = TransactionFactory.create(amount=25 * fill2_3_price, to_goal=self.goal2)
        ExecutionDistributionFactory.create(execution=execution2, transaction=transaction2, volume=25,
                                            execution_request=er2)

        execution3 = ExecutionFactory.create(asset=order2_3.ticker,
                                             volume=25,
                                             price=fill2_3_price,
                                             amount=25 * fill2_3_price)
        ExecutionApexFillFactory.create(apex_fill=apex_fill2_3, execution=execution3)
        transaction3 = TransactionFactory.create(amount=25 * fill2_3_price, to_goal=self.goal2)
        ExecutionDistributionFactory.create(execution=execution3, transaction=transaction3, volume=25,
                                            execution_request=er3)

        sum_volume = Execution.objects.filter(distributions__execution_request__asset=self.ticker2)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 50)

    def test_create_executions_eds_transactions_from_apex_fills(self):
        #out
        mor1 = MarketOrderRequestFactory.create(account=self.account1)
        ExecutionRequestFactory.create(goal=self.goal1, asset=self.ticker1, volume=100, order=mor1)

        mor2 = MarketOrderRequestFactory.create(account=self.account2)
        ExecutionRequestFactory.create(goal=self.goal2, asset=self.ticker2, volume=25, order=mor2)

        mor3 = MarketOrderRequestFactory.create(account=self.account3)
        ExecutionRequestFactory.create(goal=self.goal3, asset=self.ticker2, volume=25, order=mor3)

        create_apex_orders()

        #in
        order1 = ApexOrder.objects\
            .get(ticker=self.ticker1, morsAPEX__market_order_request__state=MarketOrderRequest.State.SENT.value)
        ApexFillFactory.create(apex_order=order1, volume=20, price=15)
        ApexFillFactory.create(apex_order=order1, volume=20, price=16)
        ApexFillFactory.create(apex_order=order1, volume=20, price=17)
        ApexFillFactory.create(apex_order=order1, volume=20, price=18)
        ApexFillFactory.create(apex_order=order1, volume=20, price=19)

        create_executions_eds_transactions_from_apex_fills()

        sum_volume = ExecutionDistribution.objects.all()\
            .filter(execution_request__goal=self.goal1)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 100)

