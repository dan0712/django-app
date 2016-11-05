from django.db import models
import logging

logger = logging.getLogger('execution.models')


class ETNALogin(models.Model):
    ResponseCode = models.PositiveIntegerField()
    Ticket = models.CharField(max_length=521)
    Result = models.OneToOneField('Result', related_name='ETNALogin')
    date_created = models.DateTimeField(auto_now_add=True)


class Result(models.Model):
    SessionId = models.CharField(max_length=128)
    UserId = models.PositiveIntegerField()
