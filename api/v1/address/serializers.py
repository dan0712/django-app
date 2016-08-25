import logging

from django.core.exceptions import ObjectDoesNotExist
from django.template import loader
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers

from api.v1.serializers import ReadOnlyModelSerializer
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

# we should use some api on the backend for addresses
# not really sure if we want to serve write or update
# endpoints for region and address
