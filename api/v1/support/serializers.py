from datetime import date
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class RequestAdvisorSupportSerializer(serializers.Serializer):
    url = serializers.CharField()
    text = serializers.CharField(required=False)
