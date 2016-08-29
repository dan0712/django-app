from django.test import TestCase

from api.v1.tests.factories import InvestmentTypeFactory, AssetClassFactory, TickerFactory


class TickerTests(TestCase):
    def setUp(self):
        self.bonds_type = InvestmentTypeFactory.create(name='BONDS')
        self.stocks_type = InvestmentTypeFactory.create(name='STOCKS')
        self.stocks_asset_class = AssetClassFactory.create(investment_type=self.stocks_type)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class)

    def test_is_stock(self):
        """
        Check that Tickers attached to stock InvestmentTypes return
        True, False otherwise.
        """
        self.assertTrue(self.stocks_ticker.is_stock)
