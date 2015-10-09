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
    # views =

    def __str__(self):
        return self.name


class PortfolioByRisk(models.Model):
    portfolio_set = models.ForeignKey(PortfolioSet, related_name="risk_profiles")
    risk = models.FloatField()
    expected_return = models.FloatField()
    volatility = models.FloatField()
    allocations = models.TextField(default="{}")


class View(models.Model):
    q = models.FloatField()
    assets = models.TextField()
    portfolio_set = models.ForeignKey(PortfolioSet, related_name="views")


class MarketCap(models.Model):
    ticker = models.OneToOneField(Ticker, related_name='market_cap')
    value = models.FloatField(default=0)
