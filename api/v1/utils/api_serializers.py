from django.core.cache import *
from django.db.models import Count
from main.models import *
from django.db.models import Count, Min, Sum, Avg
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class AdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advisor


class AccountGroupSerializer(serializers.ModelSerializer):
    advisor = AdvisorSerializer()
    secondary_advisors = AdvisorSerializer(many=True)

    class Meta:
        model = AccountGroup


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client


class ClientAccountSerializer(serializers.ModelSerializer):
    primary_owner = ClientSerializer()

    account_group = AccountGroupSerializer()

    class Meta:
        model = ClientAccount
