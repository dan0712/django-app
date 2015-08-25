__author__ = 'cristian'

from django.db import models
from django.contrib.auth.models import User
from .fields import ColorField


class Advisor(models.Model):
    user = models.OneToOneField(User)
    is_confirmed = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=36)


class Client(models.Model):
    user = models.OneToOneField(User)
    advisor = models.ForeignKey(Advisor, related_name="clients")
    is_confirmed = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=36)


class AssetClass(models.Model):
    name = models.CharField(max_length=255)
    display_order = models.IntegerField()
    donut_order = models.IntegerField()
    primary_color = ColorField()
    foreground_color = ColorField()
    drift_color = ColorField()
    asset_class_explanation = models.TextField()
    tickers_explanation = models.TextField()