import datetime

from django import test

from api.v1.tests.factories import GoalFactory, TickerFactory, \
    TransactionFactory, PositionLotFactory
from main.models import Execution, ExecutionDistribution, MarketOrderRequest, \
    Transaction, InvestmentType
from portfolios.providers.execution.django import ExecutionProviderDjango
from main.tests.fixture import Fixture1

class DjangoExecutionProviderTest(test.TestCase):
    def setUp(self):
        # for tickers
        self.bonds_type = InvestmentType.Standard.BONDS.get()
        self.stocks_type = InvestmentType.Standard.STOCKS.get()

    def test_get_asset_weights_held_less_than1y_with_new_postions(self):
        fund = TickerFactory.create(unit_price=2.1)
        goal = GoalFactory.create()
        today = datetime.date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        Fixture1.create_execution_details(goal, fund, 10, 2, datetime.date(2015, 6, 1))


        ep = ExecutionProviderDjango()
        vals = ep.get_asset_weights_held_less_than1y(goal, today)
        self.assertAlmostEqual(vals[fund.id], 21/goal.available_balance)

    def test_get_asset_weights_held_less_than1y_without_new_postions(self):
        fund = TickerFactory.create(unit_price=2.1)
        goal = GoalFactory.create()
        today = datetime.date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        Fixture1.create_execution_details(goal, fund, 10, 2, datetime.date(2014, 6, 1))

        ep = ExecutionProviderDjango()
        vals = ep.get_asset_weights_held_less_than1y(goal, today)
        self.assertEqual(len(vals), 0)

    def test_get_asset_weights_without_tax_winners(self):
        fund = TickerFactory.create(unit_price=3)
        goal = GoalFactory.create()
        today = datetime.date(2016, 1, 1)
        # Create a 6 month old execution, transaction and a distribution that caused the transaction
        Fixture1.create_execution_details(goal, fund, 10, 2, datetime.date(2014, 6, 1))
        Fixture1.create_execution_details(goal, fund, 10, 4, datetime.date(2015, 6, 1))

        ep = ExecutionProviderDjango()
        vals = ep.get_asset_weights_without_tax_winners(goal=goal)
        self.assertAlmostEqual(vals[fund.id], (10*3) / goal.available_balance)
