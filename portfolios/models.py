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


class PortfolioByRisk(models.Model):
    portfolio_set = models.ForeignKey(PortfolioSet)
    risk = models.FloatField()
    expected_return = models.FloatField()
    volatility = models.FloatField()
    allocations = models.TextField(default="{}")