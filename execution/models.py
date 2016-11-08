from django.db import models
import logging
from jsonfield.fields import JSONField
from common.structures import ChoiceEnum

logger = logging.getLogger('execution.models')


class ETNALogin(models.Model):
    # big caps due to serializer - response json
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


class OrderETNAManager(models.Manager):
    def is_complete(self):
        return self.filter(Status__in=OrderETNA.StatusChoice.complete_statuses())


class OrderETNA(models.Model):
    class OrderTypeChoice(ChoiceEnum):
        Market = 0
        Limit = 1

    class SideChoice(ChoiceEnum):
        Buy = 0
        Sell = 1

    class TimeInForceChoice(ChoiceEnum):
        Day = 0
        GoodTillCancel = 1
        AtTheOpening = 2
        ImmediateOrCancel = 3
        FillOrKill = 4
        GoodTillCrossing = 5
        GoodTillDate = 6

    class StatusChoice(ChoiceEnum):
        New = 'New'
        Sent = 'Sent'
        PartiallyFilled = 'PartiallyFilled'
        Filled = 'Filled'
        DoneForDay = 'DoneForDay'
        Canceled = 'Canceled'
        Replaced = 'Replaced'
        PendingCancel = 'PendingCancel'
        Stopped = 'Stopped'
        Rejected = 'Rejected'
        Suspended = 'Suspended'
        PendingNew = 'PendingNew'
        Calculated = 'Calculated'
        Expired = 'Expired'
        AcceptedForBidding = 'AcceptedForBidding'
        PendingReplace = 'PendingReplace'
        Error = 'Error'

        @classmethod
        def complete_statuses(cls):
            accessor = OrderETNA.StatusChoice
            return (accessor.Filled.value, accessor.DoneForDay.value, accessor.Canceled.value, accessor.Rejected.value,
                    accessor.Expired.value, accessor.Error.value)

    Price = models.FloatField()
    Exchange = models.CharField(default="Auto", max_length=128)
    TrailingLimitAmount = models.FloatField(default=0)
    AllOrNone = models.IntegerField(default=0)
    TrailingStopAmount = models.FloatField(default=0)
    Type = models.IntegerField(choices=OrderTypeChoice.choices(),default=OrderTypeChoice.Limit.value)
    Quantity = models.IntegerField()
    SecurityId = models.IntegerField()
    Side = models.IntegerField(choices=SideChoice.choices())
    TimeInForce = models.IntegerField(choices=TimeInForceChoice.choices(), default=TimeInForceChoice.GoodTillDate.value)
    StopPrice = models.FloatField(default=0)
    ExpireDate = models.IntegerField()

    # response fields
    # -1 not assigned - we will get order Id as response from REST and update it
    Order_Id = models.IntegerField(default=-1)
    Status = models.CharField(choices=StatusChoice.choices(), default=StatusChoice.New.value, max_length=128)
    FillPrice = models.FloatField(default=0)
    FillQuantity = models.IntegerField(default=0)
    Description = models.CharField(max_length=128)
    objects = OrderETNAManager() # ability to filter based on this, property cannot be used to filter

    @property
    def is_complete(self):
        return self.Status in self.StatusChoice.complete_statuses()
