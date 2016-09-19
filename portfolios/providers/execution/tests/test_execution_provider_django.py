import datetime

from django import test

from api.v1.tests.factories import GoalFactory, PositionFactory, TickerFactory, \
    TransactionFactory, InvestmentTypeFactory
from main.models import Execution, ExecutionDistribution, MarketOrderRequest, \
    Transaction
from portfolios.providers.execution.django import ExecutionProviderDjango


class DjangoExecutionProviderTest(test.TestCase):
    def setUp(self):
        # for tickers
        self.bonds_type = InvestmentTypeFactory.create(name='BONDS')
        self.stocks_type = InvestmentTypeFactory.create(name='STOCKS')

    def test_get_asset_weights_held_less_than1y_with_new_postions(self):
        fund = TickerFactory.create(unit_price=2.1)
        goal = GoalFactory.create()
        today = datetime.date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        order = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec = Execution.objects.create(asset=fund,
                                        volume=10,
                                        order=order,
                                        price=2,
                                        executed=datetime.date(2015, 6, 1),
                                        amount=20)
        t1 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=datetime.date(2015, 6, 1),
                                       amount=20)
        dist = ExecutionDistribution.objects.create(execution=exec, transaction=t1, volume=10)
        PositionFactory.create(goal=goal, ticker=fund, share=10)

        ep = ExecutionProviderDjango()
        vals = ep.get_asset_weights_held_less_than1y(goal, today)
        self.assertAlmostEqual(vals[fund.id], 21/goal.available_balance)

    def test_get_asset_weights_held_less_than1y_without_new_postions(self):
        fund = TickerFactory.create(unit_price=2.1)
        goal = GoalFactory.create()
        today = datetime.date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        order = MarketOrderRequest.objects.create(state=MarketOrderRequest.State.COMPLETE.value, account=goal.account)
        exec = Execution.objects.create(asset=fund,
                                        volume=10,
                                        order=order,
                                        price=2,
                                        executed=datetime.date(2014, 6, 1),
                                        amount=20)
        t1 = TransactionFactory.create(reason=Transaction.REASON_EXECUTION,
                                       to_goal=None,
                                       from_goal=goal,
                                       status=Transaction.STATUS_EXECUTED,
                                       executed=datetime.date(2014, 6, 1),
                                       amount=20)
        dist = ExecutionDistribution.objects.create(execution=exec, transaction=t1, volume=10)
        PositionFactory.create(goal=goal, ticker=fund, share=10)

        ep = ExecutionProviderDjango()
        vals = ep.get_asset_weights_held_less_than1y(goal, today)
        self.assertEqual(len(vals), 0)

    def test_get_asset_weights_held_less_than1y_postions_no_executions(self):
        """
        Test that any positions that have no executions are not flagged as less than one year.
        :return:
        """
        fund = TickerFactory.create(unit_price=2.1)
        goal = GoalFactory.create()
        today = datetime.date(2016, 1, 1)
        PositionFactory.create(goal=goal, ticker=fund, share=10)
        ep = ExecutionProviderDjango()
        vals = ep.get_asset_weights_held_less_than1y(goal, today)
        self.assertEqual(len(vals), 0)
