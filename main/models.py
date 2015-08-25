from django.db import models
from django.contrib.auth.models import User
from .fields import ColorField


class Advisor(models.Model):
    is_confirmed = models.BooleanField()
    confirmation_key = models.CharField(max_length=36)
    user = models.ForeignKey(User, unique=True)


class AssetClass(models.Model):
    name = models.CharField(max_length=255)
    display_order = models.IntegerField()
    donut_order = models.IntegerField()
    primary_color = models.CharField(max_length=10)
    foreground_color = models.CharField(max_length=10)
    drift_color = models.CharField(max_length=10)
    asset_class_explanation = models.TextField()
    tickers_explanation = models.TextField()
    display_name = models.CharField(max_length=255)
    investment_type = models.CharField(max_length=255)
    super_asset_class = models.CharField(max_length=255)


class Client(models.Model):
    is_confirmed = models.BooleanField()
    confirmation_key = models.CharField(max_length=36)
    advisor = models.ForeignKey(Advisor)
    user = models.ForeignKey(User, unique=True)


class Ticker(models.Model):
    symbol = models.CharField(max_length=10)
    display_name = models.CharField(max_length=255)
    description = models.TextField()
    ordering = models.IntegerField()
    url = models.CharField(max_length=200)
    unit_price = models.FloatField()
    asset_class = models.ForeignKey(AssetClass)

    class Meta:
        managed = False
        db_table = 'main_ticker'
