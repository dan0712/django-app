from django.test import TestCase

from api.v1.tests.factories import InvestmentTypeFactory, AssetClassFactory, ContentTypeFactory, TickerFactory


class TickerTests(TestCase):
    def setUp(self):
        self.bonds_type = InvestmentTypeFactory.create(name='BONDS')
        self.stocks_type = InvestmentTypeFactory.create(name='STOCKS')
        # ticker checks django contenttype model for some reason so
        # we have to manage this in fixtures a little, have to be unique per model
        self.content_type = ContentTypeFactory.create()
        self.bonds_asset_class = AssetClassFactory.create(investment_type=self.bonds_type)
        self.stocks_asset_class = AssetClassFactory.create(investment_type=self.stocks_type)
        self.bonds_ticker = TickerFactory.create(asset_class=self.bonds_asset_class, benchmark_content_type=self.content_type)
        self.stocks_ticker = TickerFactory.create(asset_class=self.stocks_asset_class, benchmark_content_type=self.content_type)

    def test_is_stock(self):
        """
        Check that Tickers attached to stock InvestmentTypes return
        True, False otherwise.
        """
        self.assertTrue(self.stocks_ticker.is_stock)
        self.assertFalse(self.bonds_ticker.is_stock)
