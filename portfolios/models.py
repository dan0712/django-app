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
    def regions(self):
        def get_regions(x):
            return x.replace("EQUITY_", "").replace("FIXED_INCOME_", "")
        return [get_regions(asset_class.super_asset_class) for asset_class in self.asset_classes.all()]

    def __str__(self):
        return self.name


class View(models.Model):
    q = models.FloatField()
    assets = models.TextField()
    portfolio_set = models.ForeignKey(PortfolioSet, related_name="views")


class MarketCap(models.Model):
    ticker = models.OneToOneField(Ticker, related_name='market_cap')
    value = models.FloatField(default=0)
