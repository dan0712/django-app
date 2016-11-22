from django.db import models
import logging
from django.db.models import PROTECT
from jsonfield.fields import JSONField
from common.structures import ChoiceEnum
from django.db.models.deletion import CASCADE, PROTECT, SET_NULL


logger = logging.getLogger('execution.models')


class ETNALogin(models.Model):
    # big caps due to serializer - response json
    ResponseCode = models.IntegerField(db_index=True)
    Ticket = models.CharField(max_length=521)
    Result = models.OneToOneField('LoginResult', related_name='ETNALogin')
    created = models.DateTimeField(auto_now_add=True, db_index=True)


class LoginResult(models.Model):
    SessionId = models.CharField(max_length=128)
    UserId = models.PositiveIntegerField()


class AccountId(models.Model):
    ResponseCode = models.IntegerField()
    Result = JSONField()
    created = models.DateTimeField(auto_now_add=True)


class SecurityETNA(models.Model):
    symbol_id = models.IntegerField()
    Symbol = models.CharField(max_length=128)
    Description = models.CharField(max_length=128)
    Currency = models.CharField(max_length=20)
    Price = models.FloatField()
    created = models.DateTimeField(auto_now_add=True, db_index=True)
