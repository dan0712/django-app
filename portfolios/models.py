from main.models import AssetClass, Ticker
from django.db import models


class ProxyAssetClass(AssetClass):
    class Meta:
        proxy = True
        verbose_name_plural = "Asset classes"
        verbose_name = "Asset class"


class ProxyTicker(Ticker):
    class Meta:
        proxy = True
        verbose_name_plural = "Ticker"
        verbose_name = "Tickers"


class PortfolioSet(models.Model):

    name = models.CharField(max_length=100)
    asset_classes = models.ManyToManyField(AssetClass, related_name='portfolio_sets')
    risk_free_rate = models.FloatField()
    tau = models.FloatField()
    default_region_sizes = models.TextField(default="{}")
    portfolios = models.TextField(editable=False, null=True, blank=True)

    @property
    def stocks_and_bonds(self):
        has_bonds = False
        has_stocks = False

        for asset_class in self.asset_classes.all():
            if "EQUITY_" in asset_class.super_asset_class:
                has_stocks = True
            if "FIXED_INCOME_" in asset_class.super_asset_class:
                has_bonds = True

        if has_bonds and has_stocks:
            return "both"
        elif has_stocks:
            return "stocks"
        else:
            return "bonds"

    @property
    def regions(self):
        def get_regions(x):
            return x.replace("EQUITY_", "").replace("FIXED_INCOME_", "")
        return [get_regions(asset_class.super_asset_class) for asset_class in self.asset_classes.all()]

    @property
    def regions_currencies(self):
        rc = {}

        def get_regions_currencies(asset):
            region = asset.super_asset_class.replace("EQUITY_", "").replace("FIXED_INCOME_", "")
            if region not in rc:
                rc[region] = "AUD"
            ticker = asset.tickers.filter(ordering=0).first()
            if ticker.currency != "AUD":
                rc[region] = ticker.currency

        for asset_class in self.asset_classes.all():
            get_regions_currencies(asset_class)
        return rc

    def __str__(self):
        return self.name


class View(models.Model):
    q = models.FloatField()
    assets = models.TextField()
    portfolio_set = models.ForeignKey(PortfolioSet, related_name="views")


class MarketCap(models.Model):
    ticker = models.OneToOneField(Ticker, related_name='market_cap')
    value = models.FloatField(default=0)
