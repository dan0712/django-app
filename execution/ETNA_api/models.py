from django.db import models
import logging
from django.utils import timezone

logger = logging.getLogger('execution.models')


class ETNALogin(models.Model):
    ResponseCode = models.PositiveIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)

