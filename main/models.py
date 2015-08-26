from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
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


INVESTMENT_TYPES = (("BONDS", "BONDS"), ("STOCKS", "STOCKS"))


SUPER_ASSET_CLASSES = (
    # EQUITY
    ("EQUITY_AU", "EQUITY_AU"), ("EQUITY_US", "EQUITY_US"), ("EQUITY_EU", "EQUITY_EU"), ("EQUITY_EM", "EQUITY_EM"),
    ("Equity_INT", "Equity_INT"),
    # FIXED_INCOME
    ("FIXED_INCOME_AU", "FIXED_INCOME_AU"), ("FIXED_INCOME_US", "FIXED_INCOME_US"),
    ("FIXED_INCOME_EU", "FIXED_INCOME_EU"), ("FIXED_INCOME_EM", "FIXED_INCOME_EM"),
    ("FIXED_INCOME_INT", "FIXED_INCOME_INT")

)


class AssetClass(models.Model):
    name = models.CharField(max_length=255, validators=[RegexValidator(regex=r'^[0-9a-zA-Z_]+$',
                                                        message="Invalid character only accept (0-9a-zA-Z_) ")])
    display_order = models.PositiveIntegerField()
    primary_color = ColorField()
    foreground_color = ColorField()
    drift_color = ColorField()
    asset_class_explanation = models.TextField(blank=True, default="", null=False)
    tickers_explanation = models.TextField(blank=True, default="", null=False)
    display_name = models.CharField(max_length=255, blank=False, null=False)
    investment_type = models.CharField(max_length=255, choices=INVESTMENT_TYPES,  blank=False, null=False)
    super_asset_class = models.CharField(max_length=255, choices=SUPER_ASSET_CLASSES)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.name = self.name.upper()

        super(AssetClass, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Ticker(models.Model):
    symbol = models.CharField(max_length=10, blank=False, null=False, validators=[RegexValidator(regex=r'^[^ ]+$',
                                                                                  message="Invalid symbol format")])
    display_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, default="", null=False)
    ordering = models.IntegerField(blank=True, default="", null=False)
    url = models.URLField()
    unit_price = models.FloatField(default=1, editable=False)
    asset_class = models.ForeignKey(AssetClass, related_name="tickers")

    def __str__(self):
        return self.symbol

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.symbol = self.symbol.upper()

        super(Ticker, self).save(force_insert, force_update, using, update_fields)
