from django.core.cache import *
from django.db.models import Count
from main.models import *
from django.db.models import Count, Min, Sum, Avg
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
