from django.db.models import Sum
from django.test import TestCase

from api.v1.tests.factories import ExecutionRequestFactory, MarketOrderRequestFactory, \
    ClientAccountFactory, GoalFactory, TickerFactory, ApexFillFactory, ApexOrderFactory
from execution.end_of_day import *
from execution.end_of_day import create_apex_orders, process_apex_fills, send_apex_order
from main.models import ApexFill, ApexOrder


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
        #1 market_order_request, 1 execution_request, 2 fills
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
        send_apex_order(order1)
        mark_as_complete(order1)

        ApexFillFactory.create(apex_order=order1, volume=fill1_volume, price=fill1_price)
        ApexFillFactory.create(apex_order=order1, volume=fill2_volume, price=fill2_price)

        process_apex_fills()

        sum_volume = Execution.objects.filter(distributions__execution_request__goal=self.goal1)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 100)

    def test_full_in_and_out_path2(self):
        # 3 market_order_requests from 3 accounts, for 2 tickers, fill for first ticker in 2 batches,
        # 1 batch for second ticker (2 mors)
        #out

        mor1 = MarketOrderRequestFactory.create(account=self.account1)
        ExecutionRequestFactory.create(goal=self.goal1, asset=self.ticker1, volume=100, order=mor1)

        mor2 = MarketOrderRequestFactory.create(account=self.account2)
        ExecutionRequestFactory.create(goal=self.goal2, asset=self.ticker2, volume=25, order=mor2)

        mor3 = MarketOrderRequestFactory.create(account=self.account3)
        ExecutionRequestFactory.create(goal=self.goal3, asset=self.ticker2, volume=25, order=mor3)

        create_apex_orders()

        #in
        fill1a_volume = 50
        fill1a_price = 10
        fill1b_volume = 50
        fill1b_price = 15

        order1 = ApexOrder.objects.get(ticker=self.ticker1)
        send_apex_order(order1)
        mark_as_complete(order1)

        ApexFillFactory.create(apex_order=order1, volume=fill1a_volume, price=fill1a_price)
        ApexFillFactory.create(apex_order=order1, volume=fill1b_volume, price=fill1b_price)

        process_apex_fills()

        sum_volume = Execution.objects.filter(distributions__execution_request__goal=self.goal1)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 100)

        fill2_3_volume = 50
        fill2_3_price = 13
        order2_3 = ApexOrder.objects.get(ticker=self.ticker2)
        send_apex_order(order2_3)
        mark_as_complete(order2_3)
        ApexFillFactory.create(apex_order=order2_3, volume=fill2_3_volume, price=fill2_3_price)

        process_apex_fills()
        sum_volume = Execution.objects.filter(distributions__execution_request__asset=self.ticker2)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 50)

    def test_full_in_and_out_path3(self):
        # test sale as well
        mor1 = MarketOrderRequestFactory.create(account=self.account1)
        ExecutionRequestFactory.create(goal=self.goal1, asset=self.ticker1, volume=101, order=mor1)

        create_apex_orders()

        #in
        fill1a_volume = 50
        fill1a_price = 10
        fill1b_volume = 50
        fill1b_price = 15

        order1 = ApexOrder.objects.get(ticker=self.ticker1)
        send_apex_order(order1)
        mark_as_complete(order1)
        ApexFillFactory.create(apex_order=order1, volume=fill1a_volume, price=fill1a_price)
        ApexFillFactory.create(apex_order=order1, volume=fill1b_volume, price=fill1b_price)

        process_apex_fills()
        order1 = ApexOrder.objects.get(ticker=self.ticker1)
        self.assertTrue(order1.fill_info == ApexOrder.FillInfo.PARTIALY_FILLED.value)

        mor2 = MarketOrderRequestFactory.create(account=self.account1)
        ExecutionRequestFactory.create(goal=self.goal1, asset=self.ticker1, volume=-60, order=mor2)
        create_apex_orders()
        fill2_volume = -60
        fill2_price = 10
        order2 = ApexOrder.objects.get(ticker=self.ticker1, state=ApexOrder.State.PENDING.value)
        order2_id = order2.id
        send_apex_order(order2)
        mark_as_complete(order2)

        ApexFillFactory.create(apex_order=order2, volume=fill2_volume, price=fill2_price)
        process_apex_fills()
        order2 = ApexOrder.objects.get(id=order2_id)
        self.assertTrue(order2.fill_info == ApexOrder.FillInfo.FILLED.value)

