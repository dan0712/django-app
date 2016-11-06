from django.db import models
import logging
from jsonfield.fields import JSONField
from common.structures import ChoiceEnum

logger = logging.getLogger('execution.models')


class ETNALogin(models.Model):
    ResponseCode = models.IntegerField()
    Ticket = models.CharField(max_length=521)
    Result = models.OneToOneField('LoginResult', related_name='ETNALogin')
    date_created = models.DateTimeField(auto_now_add=True)


class LoginResult(models.Model):
    SessionId = models.CharField(max_length=128)
    UserId = models.PositiveIntegerField()


class AccountId(models.Model):
    ResponseCode = models.IntegerField()
    Result = JSONField()
    date_created = models.DateTimeField(auto_now_add=True)


class SecurityETNA(models.Model):
    symbol_id = models.IntegerField()
    Symbol = models.CharField(max_length=128)
    Description = models.CharField(max_length=128)
    Currency = models.CharField(max_length=20)
    Price = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True)


class OrderETNA(models.Model):
    class OrderType(ChoiceEnum):
        Market = 0,
        Limit = 1,

    class Side(ChoiceEnum):
        Buy = 0,
        Sell = 1

    class TimeInForce(ChoiceEnum):
        Day = 0,
        GoodTillCancel = 1
        AtTheOpening = 2
        ImmediateOrCancel = 3
        FillOrKill = 4
        GoodTillCrossing = 5
        GoodTillDate = 6

    Price = models.FloatField()
    Exchange = models.CharField(default="Auto", max_length=128)
    TrailingLimitAmount = models.FloatField(default=0)
    AllOrNone = models.IntegerField(default=0)
    TrailingStopAmount = models.FloatField(default=0)
    Type = models.IntegerField(choices=OrderType.choices(),default=OrderType.Limit.value)
    Quantity = models.IntegerField()
    SecurityId = models.IntegerField()
    Side = models.IntegerField(choices=Side.choices())
    TimeInForce = models.IntegerField(choices=TimeInForce.choices(), default=TimeInForce.GoodTillDate.value)
    StopPrice = models.FloatField(default=0)
    ExpireDate = models.IntegerField()
