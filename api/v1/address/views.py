import logging
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import password_reset
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import exceptions, parsers, status
from rest_framework import views
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from address.models import Region, Address
from support.models import SupportRequest
from . import serializers
from ..views import ApiViewMixin

logger = logging.getLogger('api.v1.address.views')


class RegionView(ApiViewMixin, views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.RegionSerializer

    def get(self, request, pk):
        try:
            region = Region.objects.get(pk=pk)
        except:
            logger.error('Region not found with pk %s' % pk)
            return Response('Region not found', status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.RegionSerializer(region, context={'request': request})
        return Response(serializer.data)


class AddressView(ApiViewMixin, views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.AddressSerializer

    def get(self, request, pk):
        try:
            address = Address.objects.get(pk=pk)
        except:
            logger.error('Address not found with pk %s' % pk)
            return Response('Address not found', status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.AddressSerializer(address, context={'request': request})
        return Response(serializer.data)
