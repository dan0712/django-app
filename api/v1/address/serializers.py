import logging

from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers

from api.v1.serializers import ReadOnlyModelSerializer
from client.models import Client, EmailNotificationPrefs
from main.models import Advisor, User
from support.models import SupportRequest
from address.models import Region, Address

logger = logging.getLogger('api.v1.address.serializers')


class RegionSerializer(ReadOnlyModelSerializer):
    """
    For Read (GET) requests only
    """
    class Meta:
        model = Region


class AddressSerializer(ReadOnlyModelSerializer):
    """
    For Read (GET) requests only
    """

    class Meta:
        model = Address
