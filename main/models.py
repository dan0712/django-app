from django.db import models
from django.contrib.auth.models import User
from .fields import ColorField


class Advisor(models.Model):
    is_confirmed = models.BooleanField()
    confirmation_key = models.CharField(max_length=36)
    user = models.ForeignKey(User)


class Client(models.Model):
    is_confirmed = models.BooleanField()
    confirmation_key = models.CharField(max_length=36)
    advisor = models.ForeignKey(Advisor)
    user = models.ForeignKey(User)


class AssetClass(models.Model):
    name = models.CharField(max_length=255)
    display_order = models.PositiveIntegerField()
    primary_color = ColorField()
    foreground_color = ColorField()
    drift_color = ColorField()
    asset_class_explanation = models.TextField(blank=True, default="", null=False)
    tickers_explanation = models.TextField(blank=True, default="", null=False)
    display_name = models.CharField(max_length=255, blank=False, null=False)
    investment_type = models.CharField(max_length=255)
    super_asset_class = models.CharField(max_length=255)


class Ticker(models.Model):
    symbol = models.CharField(max_length=10, blank=False, null=False)
    display_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="", null=False)
    ordering = models.IntegerField(blank=True, default="", null=False)
    url = models.URLField()
    unit_price = models.FloatField(default=1)
    asset_class = models.ForeignKey(AssetClass, related_name="tickers")
