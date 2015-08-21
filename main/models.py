__author__ = 'cristian'

from django.db import models
from django.contrib.auth.models import User


class Advisor(models.Model):
    user = models.OneToOneField(User)
    is_confirmed = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=36)


class Client(models.Model):
    user = models.OneToOneField(User)
    advisor = models.ForeignKey(Advisor, related_name="clients")
    is_confirmed = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=36)