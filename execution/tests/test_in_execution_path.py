from django.db.models import Sum
from django.test import TestCase

from api.v1.tests.factories import ExecutionRequestFactory, MarketOrderRequestFactory, \
    ClientAccountFactory, GoalFactory, TickerFactory, ApexFillFactory
from execution.end_of_day import *
from execution.end_of_day import create_apex_orders, process_apex_fills, send_etna_order, \
    mark_etna_order_as_complete
from main.models import ApexFill


class BaseTest(TestCase):
    def setUp(self):
        self.account1 = ClientAccountFactory.create()
        self.goal1 = GoalFactory.create(account=self.account1)

        self.account2 = ClientAccountFactory.create()
        self.goal2 = GoalFactory.create(account=self.account2)

        self.account3 = ClientAccountFactory.create()
        self.goal3 = GoalFactory.create(account=self.account3)

        self.ticker1 = TickerFactory.create(symbol='GOOG')
        self.ticker2 = TickerFactory.create(symbol='AAPL')
        self.ticker3 = TickerFactory.create(symbol='MSFT')

    def test_apex_fill_with_apex_order(self):
        orderA = insert_order_ETNA(price=self.ticker1.unit_price, quantity=100, ticker=self.ticker1)
        orderB = insert_order_ETNA(price=self.ticker1.unit_price, quantity=200, ticker=self.ticker2)

        ApexFillFactory.create(volume=100, price=1, etna_order=orderA)
        ApexFillFactory.create(volume=100, price=1, etna_order=orderB)
        ApexFillFactory.create(volume=100, price=1, etna_order=orderB)

        fills = ApexFill.objects.filter(etna_order_id=orderB).aggregate(sum=Sum('volume'))
        self.assertTrue(fills['sum'] == 200)

        fills = ApexFill.objects.filter(etna_order_id=orderA).aggregate(sum=Sum('volume'))
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

        order1_etna = OrderETNA.objects.get(ticker=self.ticker1)
        send_etna_order(order1_etna)
        mark_etna_order_as_complete(order1_etna)

        ApexFillFactory.create(volume=fill1_volume, price=fill1_price, etna_order=order1_etna)
        ApexFillFactory.create(volume=fill2_volume, price=fill2_price, etna_order=order1_etna)

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

        order1_etna = OrderETNA.objects.get(ticker=self.ticker1)
        send_etna_order(order1_etna)
        mark_etna_order_as_complete(order1_etna)

        ApexFillFactory.create(volume=fill1a_volume, price=fill1a_price, etna_order=order1_etna)
        ApexFillFactory.create(volume=fill1b_volume, price=fill1b_price, etna_order=order1_etna)

        process_apex_fills()

        sum_volume = Execution.objects.filter(distributions__execution_request__goal=self.goal1)\
            .aggregate(sum=Sum('volume'))
        self.assertTrue(sum_volume['sum'] == 100)

        fill2_3_volume = 50
        fill2_3_price = 13

        order2_3_etna = OrderETNA.objects.get(ticker=self.ticker2)
        send_etna_order(order2_3_etna)
        mark_etna_order_as_complete(order2_3_etna)

        ApexFillFactory.create(volume=fill2_3_volume, price=fill2_3_price, etna_order=order2_3_etna)

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

        order1_etna = OrderETNA.objects.get(ticker=self.ticker1)
        send_etna_order(order1_etna)
        mark_etna_order_as_complete(order1_etna)

        ApexFillFactory.create(volume=fill1a_volume, price=fill1a_price, etna_order=order1_etna)
        ApexFillFactory.create(volume=fill1b_volume, price=fill1b_price, etna_order=order1_etna)

        process_apex_fills()
        order1 = OrderETNA.objects.get(ticker=self.ticker1)
        self.assertTrue(order1.fill_info == OrderETNA.FillInfo.PARTIALY_FILLED.value)

        mor2 = MarketOrderRequestFactory.create(account=self.account1)
        ExecutionRequestFactory.create(goal=self.goal1, asset=self.ticker1, volume=-60, order=mor2)
        create_apex_orders()
        fill2_volume = -60
        fill2_price = 10

        order2_etna = OrderETNA.objects.get(ticker=self.ticker1, Status=OrderETNA.StatusChoice.New.value)
        send_etna_order(order2_etna)
        mark_etna_order_as_complete(order2_etna)

        ApexFillFactory.create(volume=fill2_volume, price=fill2_price, etna_order=order2_etna)
        process_apex_fills()
        order2 = OrderETNA.objects.get(id=order2_etna.id)
        self.assertTrue(order2.fill_info == OrderETNA.FillInfo.FILLED.value)
