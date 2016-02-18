from django.contrib.auth.models import User
from rest_framework import serializers

from main.models import Advisor, Client, ClientAccount, Goal

from ..user.serializers import FieldUserSerializer
from ..user.serializers import (
    UserUpdateSerializer,
    ClientUpdateSerializer,
)


__all__ = (
    'ClientSerializer', 'ClientListSerializer', 'ClientUpdateSerializer',
    'ClientAccountListSerializer', 'ClientGoalListSerializer',
)


class ClientAdvisorSerializer(serializers.ModelSerializer):
    user = FieldUserSerializer()

    class Meta:
        model = Advisor


class ClientSerializer(serializers.ModelSerializer):
    user = FieldUserSerializer()
    advisor = ClientAdvisorSerializer()
 
    class Meta:
        model = Client


class ClientListSerializer(serializers.ModelSerializer):
    """
    Light version of ClientSerializer
    """
    user = FieldUserSerializer()

    class Meta:
        model = Client
        exclude = (
            'create_date',
        )


class ClientUpdateSerializer(ClientUpdateSerializer):
    pass


class UserUpdateSerializer(UserUpdateSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
        )


class ClientAccountListSerializer(serializers.ModelSerializer):
    """
    Light version of AccountSerializer
    """
    class Meta:
        model = ClientAccount
        exclude = (
            'created_at',
        )


class ClientGoalListSerializer(serializers.ModelSerializer):
    """
    Light version of PortfolioSerializer
    """
    class Meta:
        model = Goal
        exclude = (
            'portfolios',
            'created_date', 'completion_date',
        )
